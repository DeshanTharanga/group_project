"""Append-only verification decisions; evidence must be owned by the applicant."""

from sqlalchemy import select

from app.core.errors import require
from app.database import models as m
from app.services.common import add, get, now, page, row


async def detail(ctx, app):
    result = row(app)
    result["evidence_document_ids"] = list(
        await ctx.session.scalars(
            select(m.VerificationApplicationDocument.document_id).where(
                m.VerificationApplicationDocument.application_id == app.id
            )
        )
    )
    return result


async def submit_verification(ctx, data):
    profile = await get(ctx, m.ProfessionalProfile, ctx.user.id, lock=True)
    require(
        profile.role == data["role"] and profile.registration_number == data["registration_number"]
    )
    ids = data.get("evidence_document_ids") or []
    require(
        bool(ids) and len(ids) == len(set(ids)),
        "At least one unique evidence document is required.",
        422,
        "VALIDATION_ERROR",
    )
    if data.get("organization_id"):
        member = await ctx.session.scalar(
            select(m.OrganizationMembership).where(
                m.OrganizationMembership.user_id == ctx.user.id,
                m.OrganizationMembership.organization_id == data["organization_id"],
                m.OrganizationMembership.role == profile.role,
            )
        )
        require(member is not None)
    for did in ids:
        doc = await get(ctx, m.Document, did)
        require(
            doc.owner_user_id == ctx.user.id
            and doc.document_type == "verification_evidence"
            and doc.status == "active"
        )
    existing = await ctx.session.scalar(
        select(m.VerificationApplication).where(
            m.VerificationApplication.user_id == ctx.user.id,
            m.VerificationApplication.status == "pending",
        )
    )
    require(existing is None, "An application is already pending.", 409, "CONFLICT")
    app = await add(
        ctx,
        m.VerificationApplication,
        user_id=ctx.user.id,
        **{k: v for k, v in data.items() if k != "evidence_document_ids"},
    )
    for did in ids:
        await add(
            ctx,
            m.VerificationApplicationDocument,
            application_id=app.id,
            document_id=did,
            attached_by=ctx.user.id,
        )
    profile.verification_status = "pending"
    return await detail(ctx, app)


async def own_verifications(ctx, data, **filters):
    return await page(
        ctx,
        m.VerificationApplication,
        select(m.VerificationApplication).where(m.VerificationApplication.user_id == ctx.user.id),
        filters,
    )


async def admin_verifications(ctx, data, **filters):
    ctx.admin()
    return await page(ctx, m.VerificationApplication, filters=filters)


async def verification_detail(ctx, data, application_id):
    ctx.admin()
    return await detail(ctx, await get(ctx, m.VerificationApplication, application_id))


async def decide_verification(ctx, data, application_id):
    ctx.admin()
    app = await get(ctx, m.VerificationApplication, application_id, lock=True)
    require(app.user_id != ctx.user.id, "You cannot review your own application.")
    require(
        app.status in ("pending", "more_info_requested"),
        "This application has already been decided.",
        409,
        "CONFLICT",
    )
    profile = await get(ctx, m.ProfessionalProfile, app.user_id, lock=True)
    require(
        profile.role == app.role and profile.registration_number == app.registration_number,
        "The application is stale.",
        409,
        "CONFLICT",
    )
    app.status, app.reviewed_by, app.reviewed_at, app.review_reason = (
        data["status"],
        ctx.user.id,
        now(),
        data["reason"],
    )
    profile.verification_status = data["status"]
    await add(
        ctx,
        m.VerificationDecision,
        application_id=app.id,
        reviewer_user_id=ctx.user.id,
        decision=data["status"],
        reason=data["reason"],
    )
    if app.organization_id:
        org = await get(ctx, m.Organization, app.organization_id)
        require(org.status == "active")
        member = await ctx.session.scalar(
            select(m.OrganizationMembership)
            .where(
                m.OrganizationMembership.user_id == app.user_id,
                m.OrganizationMembership.organization_id == app.organization_id,
                m.OrganizationMembership.role == app.role,
            )
            .with_for_update()
        )
        require(member is not None)
        member.status = data["status"]
        member.verified_at = now() if data["status"] == "approved" else None
    await ctx.session.flush()
    return await detail(ctx, app)
