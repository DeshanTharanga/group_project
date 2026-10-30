"""Clinical amendments preserve the original typed record and link the replacement."""

from sqlalchemy import select

from app.core.errors import require
from app.database import models as m
from app.services.common import add, get, history, now, page, patient_access, row

TYPES = {
    "condition": m.Condition,
    "diagnosis": m.Diagnosis,
    "allergy": m.Allergy,
    "note": m.ClinicalNote,
}
TITLE = {
    "condition": "condition_name",
    "diagnosis": "diagnosis_name",
    "allergy": "allergen",
    "note": "note_type",
}
FK = {
    "condition": "condition_id",
    "diagnosis": "diagnosis_id",
    "allergy": "allergy_id",
    "note": "clinical_note_id",
}


def serialize(obj, kind):
    r = row(obj)
    r["type"] = kind
    r["title"] = r.pop(TITLE[kind])
    r["description"] = (
        r.pop("note_text", None)
        if kind == "note"
        else r.pop("reaction", None)
        if kind == "allergy"
        else r.get("description")
    )
    if kind == "diagnosis":
        r["recorded_at"] = r.pop("diagnosed_at")
    return r


async def find_record(ctx, rid, lock=False):
    for kind, model in TYPES.items():
        q = select(model).where(model.id == rid)
        if lock:
            q = q.with_for_update()
        obj = await ctx.session.scalar(q)
        if obj:
            return kind, obj
    require(False, "Record not found.", 404, "NOT_FOUND")


async def list_clinical_records(ctx, data, patient_id, **filters):
    await patient_access(ctx, patient_id, "history_allergies")
    # Merge typed tables before applying bounded pagination to the combined result.
    records = []
    for kind, model in TYPES.items():
        if filters.get("type") and filters["type"] != kind:
            continue
        datecol = model.diagnosed_at if kind == "diagnosis" else model.recorded_at
        q = select(model).where(model.patient_user_id == patient_id)
        if filters.get("from"):
            q = q.where(datecol >= filters["from"])
        if filters.get("to"):
            q = q.where(datecol <= filters["to"])
        # Count separately and read only the prefix needed for the requested page.
        from sqlalchemy import func

        total = await ctx.session.scalar(select(func.count()).select_from(q.subquery()))
        limit = filters.get("page", 1) * filters.get("page_size", 20)
        records.append(
            (
                total,
                [
                    serialize(o, kind)
                    for o in await ctx.session.scalars(
                        q.order_by(datecol.desc(), model.id.desc()).limit(limit)
                    )
                ],
            )
        )
    values = sorted(
        [v for _, group in records for v in group],
        key=lambda r: (r["recorded_at"], str(r["id"])),
        reverse=True,
    )
    p, size = filters.get("page", 1), filters.get("page_size", 20)
    return {
        "items": values[(p - 1) * size : p * size],
        "page": p,
        "page_size": size,
        "total": sum(n for n, _ in records),
    }


async def create_record(ctx, data, patient_id, old=None):
    require(ctx.user.id != patient_id)
    consult = await patient_access(
        ctx, patient_id, "history_allergies", data.get("consultation_id"), write=True
    )
    kind = data["type"]
    values = {
        "patient_user_id": patient_id,
        "consultation_id": consult.id,
        "source": "doctor",
        "recorded_by": ctx.user.id,
        "organization_id": consult.organization_id,
        TITLE[kind]: data["title"],
    }
    values["diagnosed_at" if kind == "diagnosis" else "recorded_at"] = data["recorded_at"]
    require(
        data["recorded_at"] <= now(),
        "Record time cannot be in the future.",
        422,
        "VALIDATION_ERROR",
    )
    if kind in ("condition", "diagnosis"):
        values.update(description=data.get("description"), clinical_code=data.get("clinical_code"))
    elif kind == "note":
        values["note_text"] = data.get("description") or data["title"]
    else:
        values["reaction"] = data.get("description")
    if old:
        require(
            old.recorded_by == ctx.user.id and old.status == "active",
            "Only the current author can amend this record.",
            409,
            "CONFLICT",
        )
        values.update(supersedes_id=old.id, correction_reason=data["reason"])
        old.status = "superseded"
    return serialize(await add(ctx, TYPES[kind], **values), kind)


async def create_clinical_record(ctx, data, patient_id):
    return await create_record(ctx, data, patient_id)


async def replace_clinical_record(ctx, data, record_id):
    kind, old = await find_record(ctx, record_id, True)
    require(
        kind == data["type"], "A correction must keep the record type.", 422, "VALIDATION_ERROR"
    )
    return await create_record(ctx, data, old.patient_user_id, old)


async def clinical_detail(ctx, data, record_id):
    kind, obj = await find_record(ctx, record_id)
    await patient_access(ctx, obj.patient_user_id, "history_allergies")
    return serialize(obj, kind)


async def clinical_history(ctx, data, record_id, **filters):
    kind, obj = await find_record(ctx, record_id)
    await patient_access(ctx, obj.patient_user_id, "history_allergies")
    result = await history(ctx, TYPES[kind], obj, filters)
    result["items"] = [
        serialize(await get(ctx, TYPES[kind], r["id"]), kind) for r in result["items"]
    ]
    return result


async def request_correction(ctx, data, record_id):
    kind, obj = await find_record(ctx, record_id)
    ctx.own(obj.patient_user_id)
    return row(
        await add(
            ctx,
            m.RecordCorrection,
            **{FK[kind]: obj.id},
            requested_by=ctx.user.id,
            reason=data["reason"],
        )
    )


async def list_corrections(ctx, data, record_id, **filters):
    kind, obj = await find_record(ctx, record_id)
    await patient_access(ctx, obj.patient_user_id, "history_allergies")
    return await page(
        ctx,
        m.RecordCorrection,
        select(m.RecordCorrection).where(getattr(m.RecordCorrection, FK[kind]) == record_id),
        filters,
    )


async def decide_correction(ctx, data, correction_id):
    correction = await get(ctx, m.RecordCorrection, correction_id, True)
    kind = next(k for k, v in FK.items() if getattr(correction, v) is not None)
    obj = await get(ctx, TYPES[kind], getattr(correction, FK[kind]))
    require(obj.recorded_by == ctx.user.id)
    await patient_access(ctx, obj.patient_user_id, "history_allergies")
    require(
        correction.request_status in ("open", "accepted"),
        "Request already resolved.",
        409,
        "CONFLICT",
    )
    replacement = data.get("replacement_record_id")
    if data["request_status"] == "resolved":
        require(replacement is not None, "A replacement is required.", 422, "VALIDATION_ERROR")
    if replacement:
        new = await get(ctx, TYPES[kind], replacement)
        require(
            new.patient_user_id == obj.patient_user_id
            and new.recorded_by == ctx.user.id
            and new.supersedes_id == obj.id
        )
        correction.replacement_record_id, correction.replacement_record_type = new.id, kind
    (
        correction.request_status,
        correction.reviewed_by,
        correction.reviewed_at,
        correction.resolution_reason,
    ) = data["request_status"], ctx.user.id, now(), data["reason"]
    await ctx.session.flush()
    return row(correction)
