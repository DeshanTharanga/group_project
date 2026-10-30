"""Prescription lifecycle, author-owned shortcuts, and retained OCR job intake."""

from html import escape
from io import BytesIO

from sqlalchemy import delete, or_, select
from starlette.responses import Response

from app.core.errors import require
from app.database import models as m
from app.services.common import add, get, now, page, patient_access, professional, row


async def detail(ctx, prescription):
    items = list(
        await ctx.session.scalars(
            select(m.PrescriptionItem)
            .where(m.PrescriptionItem.prescription_id == prescription.id)
            .order_by(m.PrescriptionItem.created_at, m.PrescriptionItem.id)
        )
    )
    reviews = list(
        await ctx.session.scalars(
            select(m.PrescriptionReview)
            .where(m.PrescriptionReview.prescription_id == prescription.id)
            .order_by(m.PrescriptionReview.reviewed_at, m.PrescriptionReview.id)
        )
    )
    return {
        "prescription": row(prescription),
        "items": [row(i) for i in items],
        "reviews": [row(r) for r in reviews],
    }


async def readable(ctx, prescription_id, lock=False):
    p = await get(ctx, m.Prescription, prescription_id, lock)
    await patient_access(ctx, p.patient_user_id, "prescriptions")
    return p


async def writable(ctx, p, consultation_id=None):
    if p.source == "patient":
        ctx.own(p.patient_user_id)
    else:
        require(p.prescriber_user_id == ctx.user.id)
        await patient_access(
            ctx,
            p.patient_user_id,
            "prescriptions",
            consultation_id or p.consultation_id,
            write=True,
        )


async def validate_items(ctx, items, issue=False):
    require(
        1 <= len(items) <= 100, "A prescription needs 1–100 medicine rows.", 422, "VALIDATION_ERROR"
    )
    for item in items:
        require(
            bool(item.get("medicine_name_snapshot"))
            and bool(item.get("dose_text"))
            and bool(item.get("frequency")),
            "Medicine name, dose and frequency are required.",
            422,
            "VALIDATION_ERROR",
        )
        require(
            (item.get("quantity") is None) == (item.get("quantity_unit") is None),
            "Quantity and unit must be supplied together.",
            422,
            "VALIDATION_ERROR",
        )
        if issue:
            require(
                item.get("quantity") is not None and item.get("quantity_unit") is not None,
                "Quantity and unit are required for issue.",
                422,
                "VALIDATION_ERROR",
            )
        if item.get("medicine_id"):
            await get(ctx, m.Medicine, item["medicine_id"])


async def create(ctx, data, patient_id, previous=None, doctor=False):
    consult = await patient_access(
        ctx,
        patient_id,
        "prescriptions",
        data.get("consultation_id"),
        write=patient_id != ctx.user.id,
    )
    require(not doctor or consult is not None, "A doctor consultation is required.")
    source = "doctor" if consult is not None else "patient"
    if source == "patient":
        require("patient" in ctx.roles)
    await validate_items(ctx, data["items"])
    if data.get("starts_on") and data.get("ends_on"):
        require(
            data["ends_on"] >= data["starts_on"],
            "End date must follow start date.",
            422,
            "VALIDATION_ERROR",
        )
    if data.get("original_document_id"):
        doc = await get(ctx, m.Document, data["original_document_id"])
        require(
            doc.patient_user_id == patient_id
            and doc.document_type == "prescription"
            and doc.status == "active"
        )
        if source == "patient":
            require(doc.owner_user_id == ctx.user.id)
    p = await add(
        ctx,
        m.Prescription,
        patient_user_id=patient_id,
        consultation_id=consult.id if consult else None,
        prescriber_user_id=ctx.user.id if consult else None,
        source=source,
        created_by=ctx.user.id,
        claimed_prescriber=data.get("claimed_prescriber") if not consult else None,
        starts_on=data.get("starts_on"),
        ends_on=data.get("ends_on"),
        original_document_id=data.get("original_document_id"),
        previous_prescription_id=previous.id if previous else None,
        version=previous.version + 1 if previous else 1,
    )
    for item in data["items"]:
        await add(ctx, m.PrescriptionItem, prescription_id=p.id, **item)
    return await detail(ctx, p)


async def list_medicines(ctx, data, **filters):
    query = select(m.Medicine)
    if filters.get("q"):
        pattern = "%" + filters["q"] + "%"
        query = query.where(
            or_(m.Medicine.generic_name.ilike(pattern), m.Medicine.brand_name.ilike(pattern))
        )
    return await page(ctx, m.Medicine, query, filters)


async def create_medicine(ctx, data):
    ctx.admin()
    return row(await add(ctx, m.Medicine, **data, is_sample=False))


async def list_prescriptions(ctx, data, patient_id, **filters):
    await patient_access(ctx, patient_id, "prescriptions")
    result = await page(
        ctx,
        m.Prescription,
        select(m.Prescription).where(m.Prescription.patient_user_id == patient_id),
        filters,
    )
    result["items"] = [
        await detail(ctx, await get(ctx, m.Prescription, r["id"])) for r in result["items"]
    ]
    return result


async def create_prescription(ctx, data, patient_id):
    return await create(ctx, data, patient_id)


async def prescription_detail(ctx, data, prescription_id):
    return await detail(ctx, await readable(ctx, prescription_id))


async def update_draft(ctx, data, prescription_id):
    p = await readable(ctx, prescription_id, True)
    await writable(ctx, p, data.get("consultation_id"))
    require(p.status == "draft", "Only a draft can be edited.", 409, "CONFLICT")
    require(
        (data.get("consultation_id") is None)
        if p.source == "patient"
        else data.get("consultation_id", p.consultation_id) == p.consultation_id
    )
    await validate_items(ctx, data["items"])
    if data.get("starts_on") and data.get("ends_on"):
        require(
            data["ends_on"] >= data["starts_on"], "Invalid date window.", 422, "VALIDATION_ERROR"
        )
    if data.get("original_document_id"):
        doc = await get(ctx, m.Document, data["original_document_id"])
        require(
            doc.patient_user_id == p.patient_user_id
            and doc.document_type == "prescription"
            and doc.status == "active"
        )
    for key in ("claimed_prescriber", "starts_on", "ends_on", "original_document_id"):
        if key in data:
            require(key != "claimed_prescriber" or p.source == "patient")
            setattr(p, key, data[key])
    # Draft item replacement is permitted before issue; no dose schedule can refer to a draft.
    await ctx.session.execute(
        delete(m.PrescriptionItem).where(m.PrescriptionItem.prescription_id == p.id)
    )
    for item in data["items"]:
        await add(ctx, m.PrescriptionItem, prescription_id=p.id, **item)
    p.version += 1
    await ctx.session.flush()
    return await detail(ctx, p)


async def delete_draft(ctx, data, prescription_id):
    p = await readable(ctx, prescription_id, True)
    await writable(ctx, p)
    require(p.status == "draft", "Only a draft can be discarded.", 409, "CONFLICT")
    # Retain original evidence and the draft itself for traceability.
    p.status = "cancelled"
    p.status_reason = "Draft discarded"
    p.issued_at = now()
    await ctx.session.flush()
    return None


async def activate(ctx, prescription_id, source):
    p = await readable(ctx, prescription_id, True)
    require(
        p.source == source and p.status == "draft",
        "The prescription cannot be activated.",
        409,
        "CONFLICT",
    )
    await writable(ctx, p)
    values = await detail(ctx, p)
    await validate_items(ctx, values["items"], issue=source == "doctor")
    if p.previous_prescription_id and source == "doctor":
        previous = await get(ctx, m.Prescription, p.previous_prescription_id, True)
        if previous.source == "doctor" and previous.status == "active":
            require(previous.prescriber_user_id == ctx.user.id)
            previous.status = "superseded"
            previous.status_reason = "Replaced by an explicitly issued order"
            previous.version += 1
            await stop_schedules(ctx, previous.id, "cancelled")
    p.status, p.issued_at = "active", now()
    await ctx.session.flush()
    return await detail(ctx, p)


async def confirm_prescription(ctx, data, prescription_id):
    return await activate(ctx, prescription_id, "patient")


async def issue_prescription(ctx, data, prescription_id):
    return await activate(ctx, prescription_id, "doctor")


async def review_prescription(ctx, data, prescription_id):
    p = await readable(ctx, prescription_id, True)
    await professional(ctx)
    require(p.source == "patient" and p.status == "active" and p.patient_user_id != ctx.user.id)
    review = await add(
        ctx, m.PrescriptionReview, prescription_id=p.id, reviewer_user_id=ctx.user.id, **data
    )
    p.review_status, p.reviewed_by, p.reviewed_at = data["outcome"], ctx.user.id, now()
    await ctx.session.flush()
    return row(review)


async def version_prescription(ctx, data, prescription_id):
    p = await readable(ctx, prescription_id, True)
    await writable(ctx, p, data.get("consultation_id"))
    require(p.status == "active", "Only an active prescription can be versioned.", 409, "CONFLICT")
    require(p.source == "doctor", "Patient records require a new personal draft.")
    result = await create(ctx, data, p.patient_user_id, p, doctor=True)
    # Keep the original active until the replacement is explicitly issued.
    return result


async def renew_prescription(ctx, data, prescription_id):
    p = await readable(ctx, prescription_id, True)
    require(p.source == "doctor" and p.prescriber_user_id == ctx.user.id)
    return await create(ctx, data, p.patient_user_id, p, doctor=True)


async def reissue_prescription(ctx, data, prescription_id):
    p = await readable(ctx, prescription_id, True)
    require(p.source == "patient" and ctx.user.id != p.patient_user_id)
    return await create(ctx, data, p.patient_user_id, p, doctor=True)


async def stop_schedules(ctx, prescription_id, status):
    # Stop reminders in the same transaction. Existing logs remain intact.
    schedules = list(
        await ctx.session.scalars(
            select(m.MedicationSchedule)
            .join(
                m.PrescriptionItem,
                m.MedicationSchedule.prescription_item_id == m.PrescriptionItem.id,
            )
            .where(
                m.PrescriptionItem.prescription_id == prescription_id,
                m.MedicationSchedule.status.in_(["active", "paused"]),
            )
            .with_for_update(of=m.MedicationSchedule)
        )
    )
    for schedule in schedules:
        schedule.status = status
        for occurrence in await ctx.session.scalars(
            select(m.DoseOccurrence)
            .where(
                m.DoseOccurrence.schedule_id == schedule.id,
                m.DoseOccurrence.scheduled_for > now(),
                m.DoseOccurrence.status.in_(["upcoming", "due"]),
            )
            .with_for_update()
        ):
            occurrence.status = "cancelled"


async def lifecycle(ctx, data, prescription_id, status):
    p = await readable(ctx, prescription_id, True)
    await writable(ctx, p)
    require(p.status == "active", "The prescription is no longer active.", 409, "CONFLICT")
    p.status, p.status_reason = status, data["reason"]
    p.version += 1
    await stop_schedules(ctx, p.id, "completed" if status == "completed" else "cancelled")
    await ctx.session.flush()
    return await detail(ctx, p)


async def cancel_prescription(ctx, data, prescription_id):
    return await lifecycle(ctx, data, prescription_id, "cancelled")


async def discontinue_prescription(ctx, data, prescription_id):
    return await lifecycle(ctx, data, prescription_id, "discontinued")


async def complete_prescription(ctx, data, prescription_id):
    return await lifecycle(ctx, data, prescription_id, "completed")


async def prescription_history(ctx, data, prescription_id, **filters):
    p = await readable(ctx, prescription_id)
    root = p
    while root.previous_prescription_id:
        root = await get(ctx, m.Prescription, root.previous_prescription_id)
    tree = select(m.Prescription.id).where(m.Prescription.id == root.id).cte(recursive=True)
    tree = tree.union_all(
        select(m.Prescription.id).join(tree, m.Prescription.previous_prescription_id == tree.c.id)
    )
    result = await page(
        ctx,
        m.Prescription,
        select(m.Prescription).where(m.Prescription.id.in_(select(tree.c.id))),
        filters,
    )

    result["items"] = [
        await detail(ctx, await get(ctx, m.Prescription, r["id"])) for r in result["items"]
    ]
    return result


async def prescription_pdf(ctx, data, prescription_id):
    result = await detail(ctx, await readable(ctx, prescription_id))
    # ReportLab rendering is blocking and belongs off the API event loop.
    import asyncio

    def render():
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

        buf = BytesIO()
        styles = getSampleStyleSheet()
        content = []
        p = result["prescription"]
        for text in (
            "MediLink prescription",
            f"Reference: {p['id']}",
            f"Source: {p['source']} | Status: {p['status']}",
            f"Review: {p['review_status']}",
            f"Issuer ID: {p['prescriber_user_id'] or 'Patient-added; not clinically verified'}",
        ):
            content += [Paragraph(escape(text), styles["Normal"]), Spacer(1, 12)]
        for item in result["items"]:
            content += [
                Paragraph(
                    escape(
                        f"{item['medicine_name_snapshot']}: {item['dose_text']}; "
                        f"{item['frequency']}; {item['instructions'] or ''}"
                    ),
                    styles["Normal"],
                ),
                Spacer(1, 12),
            ]
        SimpleDocTemplate(buf).build(content)
        return buf.getvalue()

    return Response(
        await asyncio.to_thread(render),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="prescription-{prescription_id}.pdf"',
            "Cache-Control": "no-store",
        },
    )


async def template_detail(ctx, t):
    result = row(t)
    result["items"] = [
        row(i)
        for i in await ctx.session.scalars(
            select(m.PrescriptionTemplateItem)
            .where(m.PrescriptionTemplateItem.template_id == t.id)
            .order_by(m.PrescriptionTemplateItem.position)
        )
    ]
    return {"template": result}


async def list_templates(ctx, data, **filters):
    await professional(ctx)
    result = await page(
        ctx,
        m.PrescriptionTemplate,
        select(m.PrescriptionTemplate).where(m.PrescriptionTemplate.doctor_user_id == ctx.user.id),
        filters,
    )
    result["items"] = [
        (await template_detail(ctx, await get(ctx, m.PrescriptionTemplate, v["id"])))["template"]
        for v in result["items"]
    ]
    return result


async def create_template(ctx, data):
    await professional(ctx)
    await validate_items(ctx, data["items"])
    t = await add(
        ctx,
        m.PrescriptionTemplate,
        doctor_user_id=ctx.user.id,
        name=data["name"],
        template_type=data["template_type"],
    )
    for pos, item in enumerate(data["items"], 1):
        await add(ctx, m.PrescriptionTemplateItem, template_id=t.id, position=pos, **item)
    return await template_detail(ctx, t)


async def update_template(ctx, data, template_id):
    await professional(ctx)
    t = await get(ctx, m.PrescriptionTemplate, template_id, True)
    require(t.doctor_user_id == ctx.user.id and t.status == "active")
    if "name" in data:
        t.name = data["name"]
    if "items" in data:
        await validate_items(ctx, data["items"])
        await ctx.session.execute(
            delete(m.PrescriptionTemplateItem).where(m.PrescriptionTemplateItem.template_id == t.id)
        )
        for pos, item in enumerate(data["items"], 1):
            await add(ctx, m.PrescriptionTemplateItem, template_id=t.id, position=pos, **item)
    await ctx.session.flush()
    return await template_detail(ctx, t)


async def archive_template(ctx, data, template_id):
    await professional(ctx)
    t = await get(ctx, m.PrescriptionTemplate, template_id, True)
    require(t.doctor_user_id == ctx.user.id)
    t.status, t.archived_at = "archived", now()
    await ctx.session.flush()
    return await template_detail(ctx, t)


async def create_ocr_job(ctx, data, patient_id):
    ctx.own(patient_id)
    doc = await get(ctx, m.Document, data["original_document_id"])
    require(
        doc.owner_user_id == ctx.user.id
        and doc.patient_user_id == patient_id
        and doc.document_type == "prescription"
        and doc.status == "active"
    )
    job = await add(
        ctx,
        m.PrescriptionOCRJob,
        patient_user_id=patient_id,
        original_document_id=doc.id,
        requested_by_user_id=ctx.user.id,
    )
    await add(ctx, m.JobRun, job_key=str(job.id), job_type="prescription_ocr", status="queued")
    return row(job)


async def list_ocr_jobs(ctx, data, patient_id, **filters):
    ctx.own(patient_id)
    return await page(
        ctx,
        m.PrescriptionOCRJob,
        select(m.PrescriptionOCRJob).where(m.PrescriptionOCRJob.patient_user_id == patient_id),
        filters,
    )


async def ocr_job_detail(ctx, data, job_id):
    job = await get(ctx, m.PrescriptionOCRJob, job_id)
    ctx.own(job.patient_user_id)
    return row(job)


async def retry_ocr_job(ctx, data, job_id):
    job = await get(ctx, m.PrescriptionOCRJob, job_id, True)
    ctx.own(job.patient_user_id)
    require(
        job.status == "failed" and job.attempt_count < 3,
        "This OCR job cannot be retried.",
        409,
        "CONFLICT",
    )
    job.status, job.error_code = "queued", None
    run = await ctx.session.scalar(
        select(m.JobRun).where(m.JobRun.job_key == str(job.id)).with_for_update()
    )
    require(run is not None)
    run.status, run.last_error_code = "queued", None
    await ctx.session.flush()
    return row(job)


async def confirm_ocr_draft(ctx, data, patient_id, job_id):
    ctx.own(patient_id)
    job = await get(ctx, m.PrescriptionOCRJob, job_id, True)
    require(
        job.patient_user_id == patient_id
        and job.status == "ready_for_review"
        and job.resulting_prescription_id is None,
        "OCR output must be ready for review.",
        409,
        "CONFLICT",
    )
    prescription = await create(
        ctx, {**data, "original_document_id": job.original_document_id}, patient_id
    )
    job.status, job.resulting_prescription_id = "draft_created", prescription["prescription"]["id"]
    await ctx.session.flush()
    return {"job": row(job), "prescription": prescription}
