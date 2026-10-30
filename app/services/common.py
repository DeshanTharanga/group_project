"""Shared repository primitives, live authorization, and transaction boundaries."""

import hashlib
import json
from datetime import UTC, datetime
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, text

from app.core.errors import require
from app.database import models as m
from app.database.repository import add as add
from app.database.repository import get as get
from app.database.repository import page as page
from app.database.repository import row as row


def now():
    return datetime.now(UTC)


async def professional(ctx, role="doctor", user_id=None):
    if user_id is None:
        require(role in ctx.roles)
    uid = user_id or ctx.user.id
    user = await get(ctx, m.User, uid, lock="share")
    profile = await get(ctx, m.ProfessionalProfile, uid, lock="share")
    require(
        user.status == "active"
        and profile.role == role
        and profile.verification_status == "approved"
    )
    return profile


async def membership(ctx, org_id, role, user_id=None):
    await professional(ctx, role, user_id)
    org = await get(ctx, m.Organization, org_id, lock="share")
    require(
        org.status == "active"
        and (role != "pharmacist" or org.type == "pharmacy")
        and (role != "lab_staff" or org.type == "laboratory")
    )
    member = await ctx.session.scalar(
        select(m.OrganizationMembership)
        .where(
            m.OrganizationMembership.organization_id == org_id,
            m.OrganizationMembership.user_id == (user_id or ctx.user.id),
            m.OrganizationMembership.role == role,
            m.OrganizationMembership.status == "approved",
        )
        .with_for_update(read=True)
    )
    require(member is not None)
    return member


async def patient_access(ctx, patient_id, category=None, consultation_id=None, write=False):
    await get(ctx, m.PatientProfile, patient_id)
    if ctx.user.id == patient_id:
        require(
            not consultation_id,
            "A patient cannot submit a consultation ID.",
            422,
            "VALIDATION_ERROR",
        )
        return None
    await professional(ctx)
    query = select(m.AccessGrant).where(
        m.AccessGrant.patient_user_id == patient_id,
        m.AccessGrant.professional_user_id == ctx.user.id,
        m.AccessGrant.status == "active",
        m.AccessGrant.starts_at <= now(),
        m.AccessGrant.expires_at > now(),
    )
    if category:
        query = query.join(m.GrantCategory).where(m.GrantCategory.category == category)
    if consultation_id:
        consult = await get(ctx, m.Consultation, consultation_id, lock=write)
        require(
            consult.patient_user_id == patient_id
            and consult.doctor_user_id == ctx.user.id
            and consult.ended_at is None
        )
        query = query.where(
            m.AccessGrant.id == consult.grant_id, m.AccessGrant.allow_consultation.is_(True)
        )
    else:
        consult = None
    require(not write or consult is not None, "An active consultation is required.")
    grant = await ctx.session.scalar(query.with_for_update(read=True))
    require(grant is not None, "Current patient consent is required.")
    if grant.organization_id:
        await membership(ctx, grant.organization_id, "doctor")
    return consult


async def audit(ctx, action, target_type, target_id=None, metadata=None):
    await add(
        ctx,
        m.AuditEvent,
        actor_user_id=ctx.user.id if ctx.user else None,
        actor_client_id=ctx.client.id if ctx.client else None,
        action=action,
        target_type=target_type,
        target_id=target_id,
        outcome="success",
        request_id=ctx.request.state.request_id,
        event_metadata=metadata or {},
    )


async def _invoke(
    ctx,
    operation,
    handler,
    data=None,
    params=None,
    response_model=None,
    status=200,
    idempotent=False,
):
    """Validate the response and commit it with the mutation and replay record atomically."""
    params = params or {}
    key = ctx.request.headers.get("Idempotency-Key")
    if (
        operation
        in ("onboard", "create_share", "create_lab_request", "create_client", "rotate_client")
        or ctx.request.method == "GET"
    ):
        # One-time secrets and reads are never persisted. Onboarding is a unique-UID upsert.
        key = None
    if idempotent:
        require(
            key is not None and 8 <= len(key) <= 128,
            "An Idempotency-Key of 8–128 characters is required.",
            422,
            "VALIDATION_ERROR",
        )
    record = None
    if key:
        require(8 <= len(key) <= 128, "Invalid Idempotency-Key.", 422, "VALIDATION_ERROR")
        scope = f"{ctx.actor_type}:{ctx.actor_id}:{operation}:{ctx.request.url.path}:{key}"
        # PostgreSQL advisory transaction lock works across API replicas and survives Redis loss.
        lock_id = int.from_bytes(hashlib.sha256(scope.encode()).digest()[:8], "big", signed=True)
        await ctx.session.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": lock_id})
        digest_data = dict(data) if isinstance(data, dict) else data
        if isinstance(digest_data, dict) and isinstance(digest_data.get("file"), bytes):
            digest_data["file"] = hashlib.sha256(digest_data["file"]).hexdigest()
        digest = hashlib.sha256(
            json.dumps(
                jsonable_encoder({"data": digest_data, "params": params}),
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        ).hexdigest()
        record = await ctx.session.scalar(
            select(m.IdempotencyRecord).where(
                m.IdempotencyRecord.actor_type == ctx.actor_type,
                m.IdempotencyRecord.actor_id == ctx.actor_id,
                m.IdempotencyRecord.operation_key == operation,
                m.IdempotencyRecord.target_key == ctx.request.url.path,
                m.IdempotencyRecord.idempotency_key == key,
            )
        )
        if record:
            require(
                record.request_digest == digest,
                "This key was used for a different request.",
                409,
                "IDEMPOTENCY_MISMATCH",
            )
            # Handler-specific live authorization must still run before clinical replay.
            from app.services.replay import authorize_replay

            await authorize_replay(ctx, operation, record.response_body, params)
            await audit(ctx, operation + "_replay", "api_operation")
            await ctx.session.commit()
            return record.response_body
    result = await handler(ctx, data, **params)
    await ctx.session.flush()
    if response_model:
        result = response_model.model_validate(result).model_dump(mode="json")
    if key:
        from datetime import timedelta

        await add(
            ctx,
            m.IdempotencyRecord,
            actor_type=ctx.actor_type,
            actor_id=ctx.actor_id,
            operation_key=operation,
            target_key=ctx.request.url.path,
            idempotency_key=key,
            request_digest=digest,
            response_status=status,
            response_body=jsonable_encoder(result),
            expires_at=now() + timedelta(days=1),
        )
    # Audit metadata contains no request payload or patient notes.
    if ctx.user is not None or ctx.client is not None:
        patient_id = params.get("patient_id")
        projection = result if isinstance(result, dict) else {}
        header = projection.get("prescription", projection.get("schedule", projection))
        if isinstance(header, dict) and header.get("patient_user_id"):
            patient_id = UUID(str(header["patient_user_id"]))
        if patient_id:
            await audit(ctx, operation, "patient", patient_id)
        else:
            target = projection.get("id")
            await audit(ctx, operation, operation, UUID(str(target)) if target else None)
    await ctx.session.commit()
    ctx.session.info.pop("new_files", None)
    return result


async def history(ctx, model, obj, filters):
    root = obj
    for _ in range(1000):
        if root.supersedes_id is None:
            break
        root = await get(ctx, model, root.supersedes_id)
    tree = select(model.id).where(model.id == root.id).cte(recursive=True)
    tree = tree.union_all(select(model.id).join(tree, model.supersedes_id == tree.c.id))
    return await page(ctx, model, select(model).where(model.id.in_(select(tree.c.id))), filters)


async def invoke(
    ctx,
    operation,
    handler,
    data=None,
    params=None,
    response_model=None,
    status=200,
    idempotent=False,
):
    """Keep failure audit separate from the rolled-back business transaction."""
    user_id = ctx.user.id if ctx.user else None
    client_id = ctx.client.id if ctx.client else None
    try:
        return await _invoke(
            ctx, operation, handler, data, params, response_model, status, idempotent
        )
    except Exception as exc:
        import asyncio

        from app.core.errors import DomainError

        await ctx.session.rollback()
        for path in ctx.session.info.pop("new_files", []):
            await asyncio.to_thread(path.unlink, missing_ok=True)
        if user_id or client_id:
            try:
                await add(
                    ctx,
                    m.AuditEvent,
                    actor_user_id=user_id,
                    actor_client_id=client_id,
                    action=operation,
                    target_type="api_operation",
                    outcome="failure",
                    request_id=ctx.request.state.request_id,
                    event_metadata={
                        "code": exc.code if isinstance(exc, DomainError) else "OPERATION_FAILED"
                    },
                )
                await ctx.session.commit()
            except Exception:
                # An unavailable audit database cannot turn a failed action into a success.
                await ctx.session.rollback()
        raise
