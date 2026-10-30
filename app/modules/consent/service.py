"""Consent is always read from PostgreSQL; expiry/revocation takes effect immediately."""

from datetime import timedelta

from sqlalchemy import select

from app.core.errors import require
from app.database import models as m
from app.services.common import add, get, membership, now, page, professional, row

CATEGORIES = {
    "history_allergies",
    "prescriptions",
    "reports",
    "measurements_vaccinations",
    "adherence",
}


async def doctor_qr(ctx, data):
    profile = await professional(ctx)
    return {"doctor_reference": profile.doctor_reference, "qr_payload": profile.doctor_reference}


async def doctor_from_reference(ctx, reference):
    profile = await ctx.session.scalar(
        select(m.ProfessionalProfile).where(m.ProfessionalProfile.doctor_reference == reference)
    )
    require(profile is not None, "Doctor not found.", 404, "NOT_FOUND")
    await professional(ctx, user_id=profile.user_id)
    return profile


async def resolve_doctor(ctx, data):
    profile = await doctor_from_reference(ctx, data["doctor_reference"])
    user = await get(ctx, m.User, profile.user_id)
    return {
        "user_id": user.id,
        "display_name": user.display_name,
        "role": "doctor",
        "verification_status": profile.verification_status,
    }


async def grant_detail(ctx, grant):
    cats = list(
        await ctx.session.scalars(
            select(m.GrantCategory.category).where(m.GrantCategory.grant_id == grant.id)
        )
    )
    return {"grant": row(grant), "categories": cats}


async def create_grant(ctx, data):
    await get(ctx, m.PatientProfile, ctx.user.id)
    require("patient" in ctx.roles)
    profile = await doctor_from_reference(ctx, data["doctor_reference"])
    require(profile.user_id != ctx.user.id)
    categories = data["categories"]
    require(
        set(categories) <= CATEGORIES and len(categories) == len(set(categories)),
        "Invalid or duplicate grant categories.",
        422,
        "VALIDATION_ERROR",
    )
    if data.get("organization_id"):
        await membership(ctx, data["organization_id"], "doctor", profile.user_id)
    grant = await add(
        ctx,
        m.AccessGrant,
        patient_user_id=ctx.user.id,
        professional_user_id=profile.user_id,
        organization_id=data.get("organization_id"),
        allow_consultation=data.get("allow_consultation", False),
        expires_at=now() + timedelta(hours=data["duration_hours"]),
    )
    for category in categories:
        await add(ctx, m.GrantCategory, grant_id=grant.id, category=category)
    return await grant_detail(ctx, grant)


async def own_grants(ctx, data, **filters):
    result = await page(
        ctx,
        m.AccessGrant,
        select(m.AccessGrant).where(m.AccessGrant.patient_user_id == ctx.user.id),
        filters,
    )
    result["items"] = [
        await grant_detail(ctx, await get(ctx, m.AccessGrant, r["id"])) for r in result["items"]
    ]
    return result


async def revoke_grant(ctx, data, grant_id):
    grant = await get(ctx, m.AccessGrant, grant_id, lock=True)
    ctx.own(grant.patient_user_id)
    grant.status, grant.revoked_at = "revoked", now()
    await ctx.session.flush()
    return await grant_detail(ctx, grant)


async def patient_queue(ctx, data, **filters):
    await professional(ctx)
    query = select(m.AccessGrant).where(
        m.AccessGrant.professional_user_id == ctx.user.id,
        m.AccessGrant.status == "active",
        m.AccessGrant.starts_at <= now(),
        m.AccessGrant.expires_at > now(),
    )
    result = await page(ctx, m.AccessGrant, query, filters)
    items = []
    for r in result["items"]:
        if r["organization_id"]:
            await membership(ctx, r["organization_id"], "doctor")
        user = await get(ctx, m.User, r["patient_user_id"])
        gd = await grant_detail(ctx, await get(ctx, m.AccessGrant, r["id"]))
        items.append(
            {
                "patient": {
                    "patient_user_id": user.id,
                    "display_name": user.display_name,
                    "date_of_birth": (await get(ctx, m.PatientProfile, user.id)).date_of_birth,
                },
                "grant_id": r["id"],
                "categories": gd["categories"],
                "allow_consultation": r["allow_consultation"],
                "expires_at": r["expires_at"],
            }
        )
    result["items"] = items
    return result
