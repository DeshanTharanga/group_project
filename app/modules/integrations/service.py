"""Server-to-server laboratory keys are hashed, scoped, expiring, and revocable."""

import secrets

from app.core.errors import require
from app.core.security import digest
from app.database import models as m
from app.modules.audit.service import privileged
from app.modules.documents import service as documents
from app.services.common import add, get, now, page, row


async def laboratory(ctx, org_id):
    org = await get(ctx, m.Organization, org_id)
    require(org.type == "laboratory" and org.status == "active")
    return org


async def create_client(ctx, data):
    privileged(ctx)
    await laboratory(ctx, data["organization_id"])
    require(
        data["scopes"] == ["reports:write"] and data["expires_at"] > now(),
        "Scope must be reports:write and expiry must be future.",
        422,
        "VALIDATION_ERROR",
    )
    secret = secrets.token_urlsafe(48)
    client = await add(
        ctx,
        m.IntegrationClient,
        **data,
        credential_hash=digest(secret),
        created_by=ctx.user.id,
        status="active",
    )
    return {"client": row(client), "credential": secret}


async def list_clients(ctx, data, **filters):
    ctx.admin(super_only=True)
    return await page(ctx, m.IntegrationClient, filters=filters)


async def rotate_client(ctx, data, client_id):
    privileged(ctx)
    client = await get(ctx, m.IntegrationClient, client_id, True)
    require(client.status != "revoked" and data["expires_at"] > now())
    await laboratory(ctx, client.organization_id)
    secret = secrets.token_urlsafe(48)
    client.credential_hash, client.expires_at = digest(secret), data["expires_at"]
    await ctx.session.flush()
    return {"client": row(client), "credential": secret}


async def revoke_client(ctx, data, client_id):
    privileged(ctx)
    client = await get(ctx, m.IntegrationClient, client_id, True)
    client.status, client.revoked_at = "revoked", now()
    await ctx.session.flush()
    return row(client)


async def suspend_client(ctx, data, client_id):
    privileged(ctx)
    client = await get(ctx, m.IntegrationClient, client_id, True)
    require(client.status != "revoked")
    client.status = "suspended"
    await ctx.session.flush()
    return row(client)


async def list_submissions(ctx, data, **filters):
    ctx.admin()
    return await page(ctx, m.IntegrationSubmission, filters=filters)


async def submit(ctx, data, old=None):
    await laboratory(ctx, ctx.client.organization_id)
    req = await documents.active_request(
        ctx, token=data["request_token"], lab_id=ctx.client.organization_id, lock=True
    )
    if old:
        require(
            old.patient_user_id == req.patient_user_id
            and old.laboratory_id == req.laboratory_id
            and old.source == "integration"
        )
    doc = await documents.save_document(
        ctx,
        {"file": data["file"], "filename": data["filename"], "document_type": "report"},
        req.patient_user_id,
        integration=True,
    )
    report = await documents.publish(
        ctx,
        {**data, "document_id": doc.id, "upload_request_id": req.id},
        req.patient_user_id,
        old,
        client=True,
    )
    if old:
        req.status, req.used_at = "used", now()
    submission = await add(
        ctx,
        m.IntegrationSubmission,
        client_id=ctx.client.id,
        upload_request_id=req.id,
        external_report_id=data["external_report_id"],
        idempotency_key=ctx.request.headers["Idempotency-Key"],
        status="accepted",
        report_id=report.id,
    )
    return row(submission)


async def integration_report(ctx, data):
    return await submit(ctx, data)


async def integration_report_version(ctx, data, report_id):
    old = await get(ctx, m.Report, report_id, True)
    return await submit(ctx, data, old)
