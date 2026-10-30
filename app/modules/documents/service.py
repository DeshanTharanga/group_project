"""Private evidence/report storage, one-time laboratory requests, retained report versions."""

import secrets
from datetime import timedelta
from pathlib import Path

from sqlalchemy import select
from starlette.responses import FileResponse

from app.core.errors import require
from app.core.security import digest
from app.database import models as m
from app.modules.dispensing.service import patient_identity
from app.modules.documents.storage import content_path, persist
from app.services.common import (
    add,
    audit,
    get,
    history,
    membership,
    now,
    page,
    patient_access,
    professional,
    row,
)


async def create_lab_request(ctx, data):
    await get(ctx, m.PatientProfile, ctx.user.id)
    lab = await get(ctx, m.Organization, data["laboratory_id"])
    require(lab.status == "active" and lab.type == "laboratory")
    token = secrets.token_urlsafe(32)
    req = await add(
        ctx,
        m.LabUploadRequest,
        patient_user_id=ctx.user.id,
        laboratory_id=lab.id,
        request_token_hash=digest(token),
        expires_at=now() + timedelta(days=7),
    )
    return {"request": row(req), "request_token": token}


async def own_lab_requests(ctx, data, **filters):
    return await page(
        ctx,
        m.LabUploadRequest,
        select(m.LabUploadRequest).where(m.LabUploadRequest.patient_user_id == ctx.user.id),
        filters,
    )


async def revoke_lab_request(ctx, data, request_id):
    req = await get(ctx, m.LabUploadRequest, request_id, True)
    ctx.own(req.patient_user_id)
    require(req.status == "active", "Only unused requests may be revoked.", 409, "CONFLICT")
    req.status = "revoked"
    await ctx.session.flush()
    return row(req)


async def active_request(
    ctx, request_id=None, token=None, patient_id=None, lab_id=None, lock=False
):
    query = select(m.LabUploadRequest)
    query = (
        query.where(m.LabUploadRequest.id == request_id)
        if request_id
        else query.where(m.LabUploadRequest.request_token_hash == digest(token))
    )
    if lock:
        query = query.with_for_update()
    req = await ctx.session.scalar(query)
    require(req is not None, "Upload request not found.", 404, "NOT_FOUND")
    require(
        req.status == "active" and req.expires_at > now(),
        "The upload request is expired or already consumed.",
        409,
        "CONFLICT",
    )
    require(patient_id is None or req.patient_user_id == patient_id)
    require(lab_id is None or req.laboratory_id == lab_id)
    lab = await get(ctx, m.Organization, req.laboratory_id)
    require(lab.status == "active" and lab.type == "laboratory")
    return req


async def resolve_lab_request(ctx, data):
    await membership(ctx, data["laboratory_id"], "lab_staff")
    req = await active_request(ctx, token=data["request_token"], lab_id=data["laboratory_id"])
    return {
        "request_id": req.id,
        "patient": await patient_identity(ctx, req.patient_user_id),
        "laboratory_id": req.laboratory_id,
        "expires_at": req.expires_at,
    }


async def save_document(ctx, data, patient_id=None, verification=False, integration=False):
    source = "patient"
    if verification:
        require(
            data["document_type"] == "verification_evidence" and not data.get("upload_request_id")
        )
        owner = ctx.user.id
    elif integration:
        source = "integration"
        owner = patient_id
    else:
        await get(ctx, m.PatientProfile, patient_id)
        owner = patient_id
        require(data["document_type"] in ("prescription", "report"))
        if ctx.user.id != patient_id:
            require(data.get("upload_request_id") is not None and data["document_type"] == "report")
            req = await active_request(
                ctx, request_id=data["upload_request_id"], patient_id=patient_id
            )
            await membership(ctx, req.laboratory_id, "lab_staff")
            source = "laboratory"
        else:
            require(
                not data.get("upload_request_id"),
                "Patient uploads do not use laboratory authorization.",
                422,
                "VALIDATION_ERROR",
            )
    if data.get("supersedes_id"):
        old = await get(ctx, m.Document, data["supersedes_id"])
        require(
            old.patient_user_id == patient_id
            and old.owner_user_id == owner
            and old.document_type == data["document_type"]
        )
        if not integration:
            require(old.uploaded_by == ctx.user.id or old.owner_user_id == ctx.user.id)
    key, media, sha = await persist(ctx, data["file"])
    doc = await add(
        ctx,
        m.Document,
        owner_user_id=owner,
        patient_user_id=patient_id,
        uploaded_by=ctx.user.id if ctx.user else None,
        source=source,
        document_type=data["document_type"],
        original_filename=Path(data.get("filename", "upload").replace("\\", "/")).name[:200],
        storage_key=key,
        media_type=media,
        byte_size=len(data["file"]),
        sha256=sha,
        supersedes_id=data.get("supersedes_id"),
    )
    if data.get("verification_application_id"):
        require(verification)
        app = await get(ctx, m.VerificationApplication, data["verification_application_id"], True)
        require(app.user_id == ctx.user.id and app.status in ("pending", "more_info_requested"))
        await add(
            ctx,
            m.VerificationApplicationDocument,
            application_id=app.id,
            document_id=doc.id,
            attached_by=ctx.user.id,
        )
    return doc


async def upload_document(ctx, data, patient_id):
    return row(await save_document(ctx, data, patient_id))


async def upload_verification_document(ctx, data):
    return row(await save_document(ctx, data, verification=True))


async def authorize_document(ctx, doc):
    if doc.document_type == "verification_evidence":
        if doc.owner_user_id == ctx.user.id:
            return
        ctx.admin()
        linked = await ctx.session.scalar(
            select(m.VerificationApplicationDocument.application_id).where(
                m.VerificationApplicationDocument.document_id == doc.id
            )
        )
        require(linked is not None)
        return
    if doc.patient_user_id == ctx.user.id:
        return
    report = await ctx.session.scalar(select(m.Report).where(m.Report.document_id == doc.id))
    if report is not None:
        if "lab_staff" in ctx.roles and report.laboratory_id:
            await membership(ctx, report.laboratory_id, "lab_staff")
            require(report.source in ("laboratory", "integration"))
            return
        await patient_access(ctx, doc.patient_user_id, "reports")
        return
    p = await ctx.session.scalar(
        select(m.Prescription).where(m.Prescription.original_document_id == doc.id)
    )
    require(p is not None)
    await patient_access(ctx, p.patient_user_id, "prescriptions")


async def document_detail(ctx, data, document_id):
    doc = await get(ctx, m.Document, document_id)
    await authorize_document(ctx, doc)
    return row(doc)


async def document_content(ctx, data, document_id):
    doc = await get(ctx, m.Document, document_id)
    await authorize_document(ctx, doc)
    # Keep this an attachment; no public URLs or static mount.
    return FileResponse(
        content_path(doc.storage_key),
        media_type=doc.media_type,
        filename=doc.original_filename,
        headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"},
    )


async def publish(ctx, data, patient_id, old=None, client=False):
    doc = await get(ctx, m.Document, data["document_id"], True)
    require(
        doc.patient_user_id == patient_id
        and doc.document_type == "report"
        and doc.status == "active"
    )
    req = None
    lab_id = None
    source = "patient"
    identity_id = None
    if old:
        require(
            old.status == "active" and old.document_id != doc.id,
            "Use a new file and the current report.",
            409,
            "CONFLICT",
        )
        if old.source == "patient":
            ctx.own(patient_id)
            require(doc.owner_user_id == ctx.user.id and doc.source == "patient")
        else:
            lab_id = old.laboratory_id
            if client:
                require(ctx.client.organization_id == lab_id)
            else:
                await membership(ctx, lab_id, "lab_staff")
            identity_id = old.report_identity_id
            source = old.source
        require(doc.source == source and (client or doc.uploaded_by == ctx.user.id))
        old.status = "superseded"
    elif ctx.user and ctx.user.id == patient_id:
        require(
            doc.owner_user_id == ctx.user.id
            and doc.source == "patient"
            and not data.get("upload_request_id")
        )
    else:
        require(data.get("upload_request_id") is not None)
        req = await active_request(
            ctx, request_id=data["upload_request_id"], patient_id=patient_id, lock=True
        )
        lab_id = req.laboratory_id
        if client:
            require(ctx.client.organization_id == lab_id)
            source = "integration"
        else:
            await membership(ctx, lab_id, "lab_staff")
            source = "laboratory"
        require(doc.source == source and (client or doc.uploaded_by == ctx.user.id))
        require(
            bool(data.get("lab_reference")),
            "Laboratory reference is required.",
            422,
            "VALIDATION_ERROR",
        )
        identity = await add(
            ctx,
            m.ReportIdentity,
            patient_user_id=patient_id,
            laboratory_id=lab_id,
            lab_reference=data["lab_reference"],
            initial_upload_request_id=req.id,
        )
        identity_id = identity.id
        req.status, req.used_at = "used", now()
    require(
        await ctx.session.scalar(select(m.Report.id).where(m.Report.document_id == doc.id)) is None,
        "This file has already been published.",
        409,
        "CONFLICT",
    )
    r = await add(
        ctx,
        m.Report,
        patient_user_id=patient_id,
        laboratory_id=lab_id,
        report_identity_id=identity_id,
        upload_request_id=req.id if req else None,
        document_id=doc.id,
        report_type=data["report_type"],
        report_date=data.get("report_date"),
        notes=data.get("notes"),
        source=source,
        uploaded_by=ctx.user.id if ctx.user else None,
        supersedes_id=old.id if old else None,
        correction_reason=data.get("reason") if old else None,
    )
    await add(
        ctx,
        m.Notification,
        user_id=patient_id,
        notification_type="report",
        title="Report available",
        body="A report was added or updated. Open MediLink to view it.",
        related_type="report",
        related_id=r.id,
        dedupe_key=f"report:{r.id}",
    )
    await audit(ctx, "report_published", "patient", patient_id)
    return r


async def publish_report(ctx, data, patient_id):
    return row(await publish(ctx, data, patient_id))


async def list_reports(ctx, data, patient_id, **filters):
    await patient_access(ctx, patient_id, "reports")
    return await page(
        ctx, m.Report, select(m.Report).where(m.Report.patient_user_id == patient_id), filters
    )


async def report_access(ctx, report):
    if report.patient_user_id == ctx.user.id:
        return
    if "lab_staff" in ctx.roles and report.laboratory_id:
        await membership(ctx, report.laboratory_id, "lab_staff")
    else:
        await patient_access(ctx, report.patient_user_id, "reports")


async def report_detail(ctx, data, report_id):
    r = await get(ctx, m.Report, report_id)
    await report_access(ctx, r)
    return row(r)


async def laboratory_reports(ctx, data, **filters):
    await professional(ctx, "lab_staff")
    allowed = (
        select(m.OrganizationMembership.organization_id)
        .join(m.Organization)
        .where(
            m.OrganizationMembership.user_id == ctx.user.id,
            m.OrganizationMembership.role == "lab_staff",
            m.OrganizationMembership.status == "approved",
            m.Organization.status == "active",
        )
    )
    return await page(
        ctx, m.Report, select(m.Report).where(m.Report.laboratory_id.in_(allowed)), filters
    )


async def replace_report(ctx, data, report_id):
    old = await get(ctx, m.Report, report_id, True)
    return row(await publish(ctx, data, old.patient_user_id, old))


async def withdraw_report(ctx, data, report_id):
    r = await get(ctx, m.Report, report_id, True)
    if r.source == "patient":
        ctx.own(r.patient_user_id)
    else:
        await membership(ctx, r.laboratory_id, "lab_staff")
    require(r.status == "active", "Only a current report may be withdrawn.", 409, "CONFLICT")
    r.status = "withdrawn"
    await ctx.session.flush()
    await audit(ctx, "report_withdrawn", "patient", r.patient_user_id)
    return row(r)


async def report_history(ctx, data, report_id, **filters):
    r = await get(ctx, m.Report, report_id)
    await report_access(ctx, r)
    return await history(ctx, m.Report, r, filters)
