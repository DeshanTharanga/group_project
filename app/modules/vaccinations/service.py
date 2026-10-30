from datetime import date

from sqlalchemy import select

from app.core.errors import require
from app.database import models as m
from app.services.common import add, get, history, page, patient_access, row


async def list_vaccinations(ctx, data, patient_id, **filters):
    await patient_access(ctx, patient_id, "measurements_vaccinations")
    return await page(
        ctx,
        m.Vaccination,
        select(m.Vaccination).where(m.Vaccination.patient_user_id == patient_id),
        filters,
    )


async def create(ctx, data, patient_id, old=None):
    require(ctx.user.id != patient_id)
    consult = await patient_access(
        ctx, patient_id, "measurements_vaccinations", data.get("consultation_id"), write=True
    )
    require(
        data["administered_on"] <= date.today(),
        "Vaccination date cannot be in the future.",
        422,
        "VALIDATION_ERROR",
    )
    require(
        not data.get("next_dose_on") or data["next_dose_on"] >= data["administered_on"],
        "Next dose must follow administration.",
        422,
        "VALIDATION_ERROR",
    )
    values = {k: v for k, v in data.items() if k not in ("consultation_id", "reason")}
    if old:
        require(old.recorded_by == ctx.user.id)
        require(
            await ctx.session.scalar(
                select(m.Vaccination.id).where(m.Vaccination.supersedes_id == old.id)
            )
            is None,
            "A replacement already exists.",
            409,
            "CONFLICT",
        )
        values.update(supersedes_id=old.id, correction_reason=data["reason"])
    return row(
        await add(
            ctx,
            m.Vaccination,
            **values,
            patient_user_id=patient_id,
            recorded_by=ctx.user.id,
            source="doctor",
            organization_id=consult.organization_id,
        )
    )


async def create_vaccination(ctx, data, patient_id):
    return await create(ctx, data, patient_id)


async def replace_vaccination(ctx, data, record_id):
    old = await get(ctx, m.Vaccination, record_id, True)
    return await create(ctx, data, old.patient_user_id, old)


async def vaccination_history(ctx, data, record_id, **filters):
    obj = await get(ctx, m.Vaccination, record_id)
    await patient_access(ctx, obj.patient_user_id, "measurements_vaccinations")
    return await history(ctx, m.Vaccination, obj, filters)
