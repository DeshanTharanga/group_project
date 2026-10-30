from sqlalchemy import select

from app.core.errors import require
from app.database import models as m
from app.services.common import add, get, membership, now, page, patient_access, professional, row


async def start_consultation(ctx, data):
    await professional(ctx)
    grant = await get(ctx, m.AccessGrant, data["grant_id"], lock=True)
    require(
        grant.professional_user_id == ctx.user.id
        and grant.status == "active"
        and grant.starts_at <= now() < grant.expires_at
        and grant.allow_consultation
    )
    if grant.organization_id:
        await membership(ctx, grant.organization_id, "doctor")
    return row(
        await add(
            ctx,
            m.Consultation,
            patient_user_id=grant.patient_user_id,
            doctor_user_id=ctx.user.id,
            organization_id=grant.organization_id,
            grant_id=grant.id,
        )
    )


async def list_consultations(ctx, data, patient_id, **filters):
    await patient_access(ctx, patient_id)
    query = select(m.Consultation).where(m.Consultation.patient_user_id == patient_id)
    if ctx.user.id != patient_id:
        query = query.where(m.Consultation.doctor_user_id == ctx.user.id)
    return await page(ctx, m.Consultation, query, filters)


async def end_consultation(ctx, data, consultation_id):
    consult = await get(ctx, m.Consultation, consultation_id, lock=True)
    require(consult.doctor_user_id == ctx.user.id)
    await professional(ctx)
    require(consult.ended_at is None, "The consultation has ended.", 409, "CONFLICT")
    consult.ended_at, consult.summary = now(), data.get("summary")
    await ctx.session.flush()
    return row(consult)
