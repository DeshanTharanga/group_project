"""Patient-confirmed schedules, append-only dose responses, and period adherence."""

from datetime import time, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import exists, func, select
from sqlalchemy.orm import aliased

from app.core.errors import require
from app.database import models as m
from app.services.common import add, get, now, page, patient_access, row


def validate_schedule(data):
    try:
        ZoneInfo(data["timezone"])
        times = [time.fromisoformat(v) for v in data["times"]]
    except (ZoneInfoNotFoundError, ValueError, TypeError):
        require(False, "Use an IANA timezone and valid local times.", 422, "VALIDATION_ERROR")
    require(
        data.get("confirmed") is True, "Explicit confirmation is required.", 422, "VALIDATION_ERROR"
    )
    require(
        1 <= len(times) <= 24
        and len(times) == len(set(times))
        and all(t.tzinfo is None and t.second == 0 and t.microsecond == 0 for t in times),
        "Provide 1–24 unique HH:MM times.",
        422,
        "VALIDATION_ERROR",
    )
    require(
        not data.get("ends_at") or data["ends_at"] >= data["starts_at"],
        "Invalid schedule window.",
        422,
        "VALIDATION_ERROR",
    )
    return times


async def schedule_detail(ctx, s):
    times = [
        row(t)
        for t in await ctx.session.scalars(
            select(m.ScheduleTime)
            .where(m.ScheduleTime.schedule_id == s.id)
            .order_by(m.ScheduleTime.time_of_day)
        )
    ]
    for t in times:
        t["time_of_day"] = t["time_of_day"].isoformat()
    return {"schedule": row(s), "times": times}


async def eligible_item(ctx, patient_id, item_id):
    item = await get(ctx, m.PrescriptionItem, item_id, True)
    prescription = await get(ctx, m.Prescription, item.prescription_id, True)
    require(
        prescription.patient_user_id == patient_id
        and prescription.status == "active"
        and not item.is_prn,
        "Only active fixed-time prescriptions can be scheduled.",
        422,
        "SCHEDULE_NOT_ELIGIBLE",
    )
    return item, prescription


async def create_schedule(ctx, data, patient_id, version=1):
    ctx.own(patient_id)
    times = validate_schedule(data)
    item, p = await eligible_item(ctx, patient_id, data["prescription_item_id"])
    local_start = data["starts_at"].astimezone(ZoneInfo(data["timezone"])).date()
    require(
        not p.starts_on or local_start >= p.starts_on,
        "Schedule precedes the prescription.",
        422,
        "VALIDATION_ERROR",
    )
    if p.ends_on:
        require(
            data.get("ends_at") is not None
            and data["ends_at"].astimezone(ZoneInfo(data["timezone"])).date() <= p.ends_on,
            "Schedule must end within the prescription period.",
            422,
            "VALIDATION_ERROR",
        )
    schedule = await add(
        ctx,
        m.MedicationSchedule,
        patient_user_id=patient_id,
        prescription_item_id=item.id,
        timezone=data["timezone"],
        starts_at=data["starts_at"],
        ends_at=data.get("ends_at"),
        confirmed_at=now(),
        version=version,
    )
    for t in times:
        await add(ctx, m.ScheduleTime, schedule_id=schedule.id, time_of_day=t)
    # Durable intent. Beat drains it only after this transaction commits.
    await add(ctx, m.JobRun, job_key=str(schedule.id), job_type="medication_tick", status="queued")
    return await schedule_detail(ctx, schedule)


async def list_schedules(ctx, data, patient_id, **filters):
    await patient_access(ctx, patient_id, "adherence")
    result = await page(
        ctx,
        m.MedicationSchedule,
        select(m.MedicationSchedule).where(m.MedicationSchedule.patient_user_id == patient_id),
        filters,
    )
    result["items"] = [
        await schedule_detail(ctx, await get(ctx, m.MedicationSchedule, r["id"]))
        for r in result["items"]
    ]
    return result


async def cancel_future(ctx, schedule_id):
    for occurrence in await ctx.session.scalars(
        select(m.DoseOccurrence)
        .where(
            m.DoseOccurrence.schedule_id == schedule_id,
            m.DoseOccurrence.scheduled_for > now(),
            m.DoseOccurrence.status.in_(["upcoming", "due"]),
        )
        .with_for_update()
    ):
        occurrence.status = "cancelled"


async def schedule_status(ctx, data, schedule_id):
    s = await get(ctx, m.MedicationSchedule, schedule_id, True)
    ctx.own(s.patient_user_id)
    require(s.status in ("active", "paused"), "This schedule is terminal.", 409, "CONFLICT")
    if data["status"] == "active":
        await eligible_item(ctx, s.patient_user_id, s.prescription_item_id)
    s.status = data["status"]
    s.version += 1
    if s.status != "active":
        await cancel_future(ctx, s.id)
    await ctx.session.flush()
    return await schedule_detail(ctx, s)


async def replace_schedule(ctx, data, schedule_id):
    s = await get(ctx, m.MedicationSchedule, schedule_id, True)
    ctx.own(s.patient_user_id)
    require(
        s.status in ("active", "paused") and data["prescription_item_id"] == s.prescription_item_id,
        "Only an active schedule for the same medicine can be replaced.",
        409,
        "CONFLICT",
    )
    s.status = "cancelled"
    await cancel_future(ctx, s.id)
    await ctx.session.flush()
    return await create_schedule(ctx, data, s.patient_user_id, s.version + 1)


async def list_occurrences(ctx, data, patient_id, **filters):
    await patient_access(ctx, patient_id, "adherence")
    query = (
        select(m.DoseOccurrence)
        .join(m.MedicationSchedule)
        .where(m.MedicationSchedule.patient_user_id == patient_id)
    )
    return await page(ctx, m.DoseOccurrence, query, filters)


async def occurrence_owner(ctx, occurrence_id, lock=False):
    o = await get(ctx, m.DoseOccurrence, occurrence_id, lock)
    s = await get(ctx, m.MedicationSchedule, o.schedule_id)
    ctx.own(s.patient_user_id)
    return o, s


async def snooze_occurrence(ctx, data, occurrence_id):
    o, s = await occurrence_owner(ctx, occurrence_id, True)
    require(
        s.status == "active"
        and o.status in ("upcoming", "due", "unreported")
        and o.scheduled_for <= now(),
        "Only a due unanswered dose can be snoozed.",
        409,
        "CONFLICT",
    )
    require(
        now() < data["snoozed_until"] <= now() + timedelta(hours=1),
        "Snooze must be within the next hour.",
        422,
        "VALIDATION_ERROR",
    )
    o.snoozed_until = data["snoozed_until"]
    await ctx.session.flush()
    return row(o)


def validate_response(data):
    if data["response"] == "taken":
        require(
            data.get("reported_taken_at") is not None and data["reported_taken_at"] <= now(),
            "Taken requires a non-future reported time.",
            422,
            "VALIDATION_ERROR",
        )
    else:
        require(
            data.get("reported_taken_at") is None,
            "Skipped cannot have a taken time.",
            422,
            "VALIDATION_ERROR",
        )


async def respond_occurrence(ctx, data, occurrence_id):
    o, s = await occurrence_owner(ctx, occurrence_id, True)
    require(
        o.status in ("upcoming", "due", "unreported") and o.scheduled_for <= now(),
        "Only a due unanswered dose accepts a response.",
        409,
        "CONFLICT",
    )
    validate_response(data)
    log = await add(ctx, m.MedicationLog, dose_occurrence_id=o.id, recorded_by=ctx.user.id, **data)
    o.status = data["response"]
    return row(log)


async def list_responses(ctx, data, occurrence_id, **filters):
    o = await get(ctx, m.DoseOccurrence, occurrence_id)
    s = await get(ctx, m.MedicationSchedule, o.schedule_id)
    await patient_access(ctx, s.patient_user_id, "adherence")
    return await page(
        ctx,
        m.MedicationLog,
        select(m.MedicationLog).where(m.MedicationLog.dose_occurrence_id == o.id),
        filters,
    )


async def correct_log(ctx, data, log_id):
    old = await get(ctx, m.MedicationLog, log_id, True)
    o, s = await occurrence_owner(ctx, old.dose_occurrence_id, True)
    require(
        await ctx.session.scalar(
            select(m.MedicationLog.id).where(m.MedicationLog.correction_of_id == old.id)
        )
        is None,
        "Correct the latest response only.",
        409,
        "CONFLICT",
    )
    validate_response(data)
    log = await add(
        ctx,
        m.MedicationLog,
        dose_occurrence_id=o.id,
        recorded_by=ctx.user.id,
        correction_of_id=old.id,
        **data,
    )
    o.status = data["response"]
    return row(log)


async def adherence(ctx, data, patient_id, **filters):
    await patient_access(ctx, patient_id, "adherence")
    start, end = filters.get("from"), filters.get("to")
    require(
        start is not None
        and end is not None
        and start <= end
        and end - start <= timedelta(days=366),
        "Provide both period bounds, up to 366 days.",
        422,
        "VALIDATION_ERROR",
    )
    replacement = aliased(m.MedicationLog)
    latest = (
        select(m.MedicationLog.dose_occurrence_id, m.MedicationLog.response)
        .where(
            ~exists(
                select(replacement.id).where(replacement.correction_of_id == m.MedicationLog.id)
            )
        )
        .subquery()
    )
    rows = await ctx.session.execute(
        select(latest.c.response, func.count())
        .select_from(m.DoseOccurrence)
        .join(m.MedicationSchedule)
        .outerjoin(latest, latest.c.dose_occurrence_id == m.DoseOccurrence.id)
        .where(
            m.MedicationSchedule.patient_user_id == patient_id,
            m.DoseOccurrence.scheduled_for >= start,
            m.DoseOccurrence.scheduled_for <= end,
            m.DoseOccurrence.scheduled_for <= now(),
            m.DoseOccurrence.status != "cancelled",
        )
        .group_by(latest.c.response)
    )
    counts = dict(rows.all())
    taken, skipped, unreported = (
        counts.get("taken", 0),
        counts.get("skipped", 0),
        counts.get(None, 0),
    )
    eligible = taken + skipped + unreported
    return {
        "period_from": start,
        "period_to": end,
        "taken": taken,
        "skipped": skipped,
        "unreported": unreported,
        "eligible": eligible,
        "percentage": round(100 * taken / eligible, 2) if eligible else None,
        "label": "Self-reported adherence",
    }
