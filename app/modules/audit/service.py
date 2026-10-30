"""Administrative operations require explicit privileges and never confer clinical access."""

from sqlalchemy import delete, func, or_, select
from sqlalchemy.dialects.postgresql import insert

from app.core.errors import require
from app.database import models as m
from app.services.common import get, now, page, row


def privileged(ctx):
    ctx.admin(super_only=True)
    firebase = ctx.identity.get("firebase", {})
    require(
        bool(firebase.get("sign_in_second_factor"))
        and now().timestamp() - ctx.identity.get("auth_time", 0) <= 600,
        "A recent Firebase MFA sign-in is required.",
        403,
        "MFA_REQUIRED",
    )


async def admin_users(ctx, data, **filters):
    ctx.admin()
    query = select(m.User)
    if filters.get("q"):
        pattern = "%" + filters["q"] + "%"
        query = query.where(or_(m.User.display_name.ilike(pattern), m.User.email.ilike(pattern)))
    return await page(ctx, m.User, query, filters)


async def set_user_status(ctx, data, user_id):
    ctx.admin()
    require(user_id != ctx.user.id, "You cannot change your own account status.")
    user = await get(ctx, m.User, user_id, True)
    roles = set(
        await ctx.session.scalars(
            select(m.Role.code)
            .join(m.UserRole, m.UserRole.role_id == m.Role.id)
            .where(m.UserRole.user_id == user_id)
        )
    )
    require(
        "super_admin" not in roles,
        "Super Admin status changes require an offline recovery process.",
    )
    if "admin" in roles:
        privileged(ctx)
    user.status = data["status"]
    await ctx.session.flush()
    return row(user)


async def assign_admin(ctx, data):
    privileged(ctx)
    user = await get(ctx, m.User, data["user_id"], True)
    require(user.status == "active")
    role = await ctx.session.scalar(select(m.Role).where(m.Role.code == "admin"))
    await ctx.session.execute(
        insert(m.UserRole)
        .values(user_id=user.id, role_id=role.id, assigned_by=ctx.user.id)
        .on_conflict_do_nothing()
    )
    return {"id": user.id, "status": "assigned", "updated_at": now()}


async def revoke_admin(ctx, data, user_id):
    privileged(ctx)
    require(user_id != ctx.user.id)
    await get(ctx, m.User, user_id, True)
    role = await ctx.session.scalar(select(m.Role).where(m.Role.code == "admin"))
    await ctx.session.execute(
        delete(m.UserRole).where(m.UserRole.user_id == user_id, m.UserRole.role_id == role.id)
    )
    return {"id": user_id, "status": "revoked", "updated_at": now()}


async def operations(ctx, data):
    ctx.admin()

    async def count(model, condition):
        return await ctx.session.scalar(select(func.count()).select_from(model).where(condition))

    return {
        "pending_verifications": await count(
            m.VerificationApplication, m.VerificationApplication.status == "pending"
        ),
        "active_organizations": await count(m.Organization, m.Organization.status == "active"),
        "failed_jobs": await count(m.JobRun, m.JobRun.status == "failed"),
        "last_backup_at": await ctx.session.scalar(
            select(func.max(m.BackupRun.finished_at)).where(m.BackupRun.status == "succeeded")
        ),
    }


def job_projection(job):
    return {
        "id": job.id,
        "job_type": job.job_type,
        "status": job.status,
        "attempt_count": job.attempt_count,
        "error_code": job.last_error_code,
        "updated_at": job.finished_at or job.started_at or job.created_at,
    }


async def list_jobs(ctx, data, **filters):
    ctx.admin()
    result = await page(ctx, m.JobRun, filters=filters)
    result["items"] = [job_projection(await get(ctx, m.JobRun, r["id"])) for r in result["items"]]
    return result


async def retry_job(ctx, data, job_id):
    ctx.admin()
    job = await get(ctx, m.JobRun, job_id, True)
    require(
        job.status == "failed"
        and job.attempt_count < 3
        and job.job_type in ("prescription_ocr", "medication_tick"),
        "Job is not retryable.",
        409,
        "CONFLICT",
    )
    if job.job_type == "prescription_ocr":
        from uuid import UUID

        ocr = await get(ctx, m.PrescriptionOCRJob, UUID(job.job_key), True)
        require(ocr.status == "failed" and ocr.resulting_prescription_id is None)
        ocr.status, ocr.error_code = "queued", None
    job.status, job.last_error_code, job.finished_at = "queued", None, None
    await ctx.session.flush()
    return job_projection(job)


async def list_audit(ctx, data, **filters):
    ctx.admin()
    require(
        "super_admin" in ctx.roles or "audit:read" in ctx.identity.get("medilink_permissions", []),
        "Delegated audit permission is required.",
    )
    return await page(ctx, m.AuditEvent, filters=filters)


async def patient_activity(ctx, data, patient_id, **filters):
    ctx.own(patient_id)
    return await page(
        ctx,
        m.AuditEvent,
        select(m.AuditEvent).where(
            m.AuditEvent.target_type == "patient", m.AuditEvent.target_id == patient_id
        ),
        filters,
    )
