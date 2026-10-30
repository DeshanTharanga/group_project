"""Sync Celery entry points create/dispose their own async engine per event loop."""

import asyncio
from datetime import UTC, datetime, timedelta
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import delete, exists, select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.database import models as m
from app.database.session import database_url
from app.services.common import now
from app.workers.celery_app import celery_app
from app.workers.ocr import OCRError, extract_text


def occurrence_times(starts_at, ends_at, times, zone, window_start, window_end):
    """Wall-clock times: skip nonexistent DST times, choose first fold once."""
    tz = ZoneInfo(zone)
    lower = max(starts_at, window_start)
    upper = min(ends_at, window_end) if ends_at else window_end
    if lower > upper:
        return []
    day = lower.astimezone(tz).date()
    last = upper.astimezone(tz).date()
    values = []
    while day <= last:
        for t in times:
            local = datetime.combine(day, t, tzinfo=tz).replace(fold=0)
            utc = local.astimezone(UTC)
            if utc.astimezone(tz).replace(tzinfo=None) != local.replace(tzinfo=None):
                continue
            if lower <= utc <= upper:
                values.append(utc)
        day += timedelta(days=1)
    return sorted(set(values))


async def medication_work(session, schedule_id=None):
    timestamp = now()
    cursor = None
    while True:
        query = (
            select(m.MedicationSchedule)
            .where(m.MedicationSchedule.status == "active")
            .order_by(m.MedicationSchedule.id)
            .limit(100)
            .with_for_update(skip_locked=True)
        )
        if cursor is not None:
            query = query.where(m.MedicationSchedule.id > cursor)
        if schedule_id:
            query = query.where(m.MedicationSchedule.id == schedule_id)
        schedules = list(await session.scalars(query))
        if not schedules:
            break
        for s in schedules:
            user = await session.get(m.User, s.patient_user_id)
            item = await session.get(m.PrescriptionItem, s.prescription_item_id)
            p = await session.get(m.Prescription, item.prescription_id)
            if user.status != "active" or p.status != "active":
                continue
            if (s.ends_at and s.ends_at < timestamp) or (
                p.ends_on and timestamp.astimezone(ZoneInfo(s.timezone)).date() > p.ends_on
            ):
                s.status = "completed"
                continue
            times = list(
                await session.scalars(
                    select(m.ScheduleTime.time_of_day).where(m.ScheduleTime.schedule_id == s.id)
                )
            )
            # Only the recent 24 hours are backfilled after downtime; never flood old alerts.
            end = s.ends_at
            if p.ends_on:
                from datetime import time

                prescription_end = datetime.combine(
                    p.ends_on, time.max, tzinfo=ZoneInfo(s.timezone)
                ).astimezone(UTC)
                end = min(end, prescription_end) if end else prescription_end
            values = occurrence_times(
                s.starts_at,
                end,
                times,
                s.timezone,
                timestamp - timedelta(days=1),
                timestamp + timedelta(days=2),
            )
            for scheduled in values:
                await session.execute(
                    insert(m.DoseOccurrence)
                    .values(schedule_id=s.id, scheduled_for=scheduled)
                    .on_conflict_do_nothing(index_elements=["schedule_id", "scheduled_for"])
                )
            # Resuming a schedule reactivates future occurrences that were cancelled while paused.
            occurrences = list(
                await session.scalars(
                    select(m.DoseOccurrence)
                    .where(
                        m.DoseOccurrence.schedule_id == s.id,
                        m.DoseOccurrence.status.in_(["upcoming", "due", "unreported", "cancelled"]),
                    )
                    .order_by(m.DoseOccurrence.scheduled_for)
                    .with_for_update()
                )
            )
            profile = await session.get(m.PatientProfile, s.patient_user_id)
            enabled = profile.notification_preferences.get("medication_in_app", True)
            for o in occurrences:
                if o.status == "cancelled":
                    if o.scheduled_for > timestamp:
                        o.status = "upcoming"
                    else:
                        continue
                if o.scheduled_for > timestamp:
                    continue
                o.status = (
                    "unreported" if o.scheduled_for < timestamp - timedelta(hours=24) else "due"
                )
                if (
                    o.scheduled_for < timestamp - timedelta(days=1)
                    or (o.snoozed_until and o.snoozed_until > timestamp)
                    or not enabled
                ):
                    continue
                key = f"dose:{o.id}" + (
                    f":snooze:{o.snoozed_until.isoformat()}" if o.snoozed_until else ""
                )
                await session.execute(
                    insert(m.Notification)
                    .values(
                        user_id=s.patient_user_id,
                        notification_type="medication",
                        title="Medication reminder",
                        body="A scheduled dose is due. Open MediLink to view it.",
                        related_type="dose_occurrence",
                        related_id=o.id,
                        dedupe_key=key,
                    )
                    .on_conflict_do_nothing(index_elements=["dedupe_key"])
                )
        cursor = schedules[-1].id
        if schedule_id or len(schedules) < 100:
            break


async def vaccination_work(session):
    from sqlalchemy.orm import aliased

    successor = aliased(m.Vaccination)
    cursor = None
    while True:
        query = (
            select(m.Vaccination)
            .where(
                m.Vaccination.next_dose_on == now().date(),
                ~exists(select(successor.id).where(successor.supersedes_id == m.Vaccination.id)),
            )
            .order_by(m.Vaccination.id)
            .limit(100)
        )
        if cursor is not None:
            query = query.where(m.Vaccination.id > cursor)
        values = list(await session.scalars(query))
        for vaccine in values:
            user = await session.get(m.User, vaccine.patient_user_id)
            profile = await session.get(m.PatientProfile, vaccine.patient_user_id)
            if user.status != "active" or not profile.notification_preferences.get(
                "vaccination_in_app", True
            ):
                continue
            await session.execute(
                insert(m.Notification)
                .values(
                    user_id=user.id,
                    notification_type="vaccination",
                    title="Vaccination reminder",
                    body="A recorded next-dose date is today. Open MediLink to view it.",
                    related_type="vaccination",
                    related_id=vaccine.id,
                    dedupe_key=f"vaccination:{vaccine.id}:{vaccine.next_dose_on}",
                )
                .on_conflict_do_nothing(index_elements=["dedupe_key"])
            )
        if len(values) < 100:
            break
        cursor = values[-1].id


async def expire_tokens(session):
    timestamp = now()
    rules = [
        (
            m.AccessGrant,
            (m.AccessGrant.status == "active") & (m.AccessGrant.expires_at <= timestamp),
        ),
        (
            m.LabUploadRequest,
            (m.LabUploadRequest.status == "active") & (m.LabUploadRequest.expires_at <= timestamp),
        ),
        (
            m.PrescriptionShare,
            (
                (m.PrescriptionShare.status.in_(["created", "claimed"]))
                & (m.PrescriptionShare.claim_expires_at <= timestamp)
            )
            | (
                (m.PrescriptionShare.status == "confirmed")
                & (m.PrescriptionShare.confirmed_access_expires_at <= timestamp)
            ),
        ),
    ]
    for model, condition in rules:
        for obj in await session.scalars(
            select(model).where(condition).limit(1000).with_for_update(skip_locked=True)
        ):
            obj.status = "expired"
    await session.execute(
        delete(m.IdempotencyRecord).where(m.IdempotencyRecord.expires_at < timestamp)
    )


async def ocr_work(session, job):
    ocr = await session.scalar(
        select(m.PrescriptionOCRJob)
        .where(m.PrescriptionOCRJob.id == UUID(job.job_key))
        .with_for_update()
    )
    if ocr is None or ocr.status != "queued":
        return
    user = await session.get(m.User, ocr.patient_user_id)
    doc = await session.get(m.Document, ocr.original_document_id)
    ocr.attempt_count += 1
    if (
        user.status != "active"
        or doc.owner_user_id != user.id
        or doc.status != "active"
        or doc.document_type != "prescription"
    ):
        raise OCRError("OCR_PERMISSION_CHANGED")
    ocr.status = "processing"
    from app.modules.documents.storage import content_path

    raw = await asyncio.to_thread(extract_text, content_path(doc.storage_key), doc.media_type)
    if not raw.strip():
        raise OCRError("OCR_NO_TEXT")
    ocr.extracted_fields = {"raw_text": raw, "items": []}
    ocr.status, ocr.error_code = "ready_for_review", None


async def run_worker(kind):
    engine = create_async_engine(database_url(), poolclass=NullPool)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with sessions() as session:
            async with session.begin():
                # Beat messages may overlap or be redelivered. Never run two scans concurrently.
                acquired = await session.scalar(
                    text("SELECT pg_try_advisory_xact_lock(:key)"),
                    {"key": 181010 if kind == "tick" else 181011},
                )
                if not acquired:
                    return
                if kind == "tick":
                    await medication_work(session)
                    await vaccination_work(session)
                    await expire_tokens(session)
                    return
                jobs = list(
                    await session.scalars(
                        select(m.JobRun)
                        .where(m.JobRun.status == "queued")
                        .order_by(m.JobRun.created_at)
                        .limit(10)
                        .with_for_update(skip_locked=True)
                    )
                )
                for job in jobs:
                    job.status, job.started_at = "running", now()
                    job.attempt_count += 1
                    try:
                        # Isolate clinical work so a failed task leaves no partial output.
                        async with session.begin_nested():
                            if job.job_type == "medication_tick":
                                await medication_work(session, UUID(job.job_key))
                            elif job.job_type == "prescription_ocr":
                                await ocr_work(session, job)
                            else:
                                raise OCRError("UNKNOWN_JOB_TYPE")
                        job.status, job.last_error_code = "succeeded", None
                    except Exception as exc:
                        job.status = "failed"
                        job.last_error_code = (
                            exc.code if isinstance(exc, OCRError) else "JOB_FAILED"
                        )
                        if job.job_type == "prescription_ocr":
                            ocr = await session.get(
                                m.PrescriptionOCRJob, UUID(job.job_key), populate_existing=True
                            )
                            if ocr:
                                ocr.status, ocr.error_code = "failed", job.last_error_code
                                ocr.attempt_count += 1
                    job.finished_at = now()
    finally:
        await engine.dispose()


@celery_app.task(
    name="medilink.drain_jobs", autoretry_for=(OSError,), retry_backoff=True, max_retries=3
)
def drain_jobs():
    asyncio.run(run_worker("jobs"))


@celery_app.task(
    name="medilink.medication_tick", autoretry_for=(OSError,), retry_backoff=True, max_retries=3
)
def medication_tick():
    asyncio.run(run_worker("tick"))
