from sqlalchemy import select

from app.core.errors import require
from app.database import models as m
from app.services.common import add, now, page, patient_access, row


def validate_measurement(data):
    units = {
        "weight": {"kg", "lb"},
        "blood_glucose": {"mmol/L", "mg/dL"},
        "blood_pressure": {"mmHg"},
    }
    require(
        data["unit"] in units[data["type"]],
        "Unit does not match measurement type.",
        422,
        "VALIDATION_ERROR",
    )
    require(data["value"] > 0, "Value must be positive.", 422, "VALIDATION_ERROR")
    if data["type"] == "blood_pressure":
        require(
            data.get("secondary_value") is not None and data["secondary_value"] > 0,
            "Blood pressure requires two positive values.",
            422,
            "VALIDATION_ERROR",
        )
    else:
        require(
            data.get("secondary_value") is None,
            "Only blood pressure has a secondary value.",
            422,
            "VALIDATION_ERROR",
        )


async def list_measurements(ctx, data, patient_id, **filters):
    await patient_access(ctx, patient_id, "measurements_vaccinations")
    return await page(
        ctx,
        m.Measurement,
        select(m.Measurement).where(m.Measurement.patient_user_id == patient_id),
        filters,
    )


async def create_measurement(ctx, data, patient_id):
    validate_measurement(data)
    await patient_access(
        ctx,
        patient_id,
        "measurements_vaccinations",
        data.get("consultation_id"),
        write=patient_id != ctx.user.id,
    )
    require(
        data["measured_at"] <= now(),
        "Measurement time cannot be in the future.",
        422,
        "VALIDATION_ERROR",
    )
    values = {k: v for k, v in data.items() if k != "consultation_id"}
    return row(
        await add(
            ctx,
            m.Measurement,
            **values,
            patient_user_id=patient_id,
            recorded_by=ctx.user.id,
            source="patient" if patient_id == ctx.user.id else "doctor",
        )
    )
