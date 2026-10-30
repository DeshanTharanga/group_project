"""Claim/confirm sharing and row-locked dispensing. Tokens are stored as hashes."""

import secrets
from datetime import timedelta
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import case, func, select

from app.core.errors import require
from app.core.security import digest
from app.database import models as m
from app.services.common import add, get, membership, now, page, professional, row


async def identity(ctx, user_id, org_id=None):
    user = await get(ctx, m.User, user_id)
    profile = await get(ctx, m.ProfessionalProfile, user_id)
    result = {
        "user_id": user.id,
        "display_name": user.display_name,
        "role": profile.role,
        "verification_status": profile.verification_status,
    }
    if org_id:
        org = await get(ctx, m.Organization, org_id)
        result.update(organization_id=org.id, organization_name=org.name)
    return result


async def patient_identity(ctx, user_id):
    user = await get(ctx, m.User, user_id)
    profile = await get(ctx, m.PatientProfile, user_id)
    return {
        "patient_user_id": user.id,
        "display_name": user.display_name,
        "date_of_birth": profile.date_of_birth,
    }


async def detail(ctx, share):
    result = {
        "share": row(share),
        "pharmacist": None,
        "access_expires_at": share.confirmed_access_expires_at,
    }
    if share.claimed_by:
        result["pharmacist"] = await identity(ctx, share.claimed_by, share.claimed_organization_id)
    return result


async def eligible_prescription(ctx, prescription_id, lock=False):
    p = await get(ctx, m.Prescription, prescription_id, lock)
    require(
        p.source == "doctor"
        and p.status == "active"
        and (p.ends_on is None or p.ends_on >= now().date()),
        "Only a current active doctor order may be shared or dispensed.",
        409,
        "CONFLICT",
    )
    return p


async def create_share(ctx, data):
    p = await eligible_prescription(ctx, data["prescription_id"], True)
    ctx.own(p.patient_user_id)
    token = secrets.token_urlsafe(32)
    share = await add(
        ctx,
        m.PrescriptionShare,
        prescription_id=p.id,
        patient_user_id=ctx.user.id,
        claim_token_hash=digest(token),
        claim_expires_at=now() + timedelta(minutes=15),
    )
    return {"share": row(share), "claim_token": token, "claim_expires_at": share.claim_expires_at}


async def own_shares(ctx, data, **filters):
    result = await page(
        ctx,
        m.PrescriptionShare,
        select(m.PrescriptionShare).where(m.PrescriptionShare.patient_user_id == ctx.user.id),
        filters,
    )

    result["items"] = [
        await detail(ctx, await get(ctx, m.PrescriptionShare, r["id"])) for r in result["items"]
    ]
    return result


async def claim_share(ctx, data):
    await membership(ctx, data["organization_id"], "pharmacist")
    share = await ctx.session.scalar(
        select(m.PrescriptionShare)
        .where(m.PrescriptionShare.claim_token_hash == digest(data["claim_token"]))
        .with_for_update()
    )
    require(share is not None, "Share not found.", 404, "NOT_FOUND")
    require(
        share.status == "created" and share.claim_expires_at > now(),
        "The share has expired or was already claimed.",
        409,
        "CONFLICT",
    )
    await eligible_prescription(ctx, share.prescription_id)
    share.status, share.claimed_by, share.claimed_organization_id, share.claimed_at = (
        "claimed",
        ctx.user.id,
        data["organization_id"],
        now(),
    )
    await ctx.session.flush()
    return await detail(ctx, share)


async def share_detail(ctx, data, share_id):
    share = await get(ctx, m.PrescriptionShare, share_id)
    require(ctx.user.id in (share.patient_user_id, share.claimed_by))
    if ctx.user.id == share.claimed_by:
        await membership(ctx, share.claimed_organization_id, "pharmacist")
    return await detail(ctx, share)


async def confirm_share(ctx, data, share_id):
    share = await get(ctx, m.PrescriptionShare, share_id, True)
    ctx.own(share.patient_user_id)
    require(
        share.status == "claimed" and share.claim_expires_at > now(),
        "This share cannot be confirmed.",
        409,
        "CONFLICT",
    )
    await membership(ctx, share.claimed_organization_id, "pharmacist", share.claimed_by)
    await eligible_prescription(ctx, share.prescription_id)
    share.status, share.confirmed_at, share.confirmed_access_expires_at = (
        "confirmed",
        now(),
        now() + timedelta(hours=24),
    )
    await ctx.session.flush()
    return await detail(ctx, share)


async def revoke_share(ctx, data, share_id):
    share = await get(ctx, m.PrescriptionShare, share_id, True)
    ctx.own(share.patient_user_id)
    share.status, share.revoked_at = "revoked", now()
    await ctx.session.flush()
    return await detail(ctx, share)


async def authorized_share(ctx, share_id, org_id=None, lock=False):
    share = await get(ctx, m.PrescriptionShare, share_id, lock or "share")
    require(
        share.claimed_by == ctx.user.id
        and share.status == "confirmed"
        and share.confirmed_access_expires_at > now(),
        "A confirmed current share is required.",
    )
    require(org_id is None or share.claimed_organization_id == org_id)
    await membership(ctx, share.claimed_organization_id, "pharmacist")
    p = await eligible_prescription(ctx, share.prescription_id, lock)
    return share, p


async def net_dispensed(ctx, item_id):
    value = await ctx.session.scalar(
        select(
            func.coalesce(
                func.sum(
                    case(
                        (m.DispensingEvent.reversal_of_id.is_not(None), -m.DispensingItem.quantity),
                        else_=m.DispensingItem.quantity,
                    )
                ),
                0,
            )
        )
        .select_from(m.DispensingItem)
        .join(m.DispensingEvent)
        .where(m.DispensingItem.prescription_item_id == item_id)
    )
    return Decimal(value)


async def shared_prescription(ctx, data, share_id):
    share, p = await authorized_share(ctx, share_id)
    values = []
    for item in await ctx.session.scalars(
        select(m.PrescriptionItem)
        .where(m.PrescriptionItem.prescription_id == p.id)
        .order_by(m.PrescriptionItem.id)
    ):
        require(
            item.quantity is not None,
            "The issued order has no dispensable quantity.",
            409,
            "CONFLICT",
        )
        total = await net_dispensed(ctx, item.id)
        values.append(
            {
                "item": row(item),
                "dispensed_quantity": total,
                "remaining_quantity": item.quantity - total,
            }
        )
    return {
        "prescription_id": p.id,
        "patient": await patient_identity(ctx, p.patient_user_id),
        "issuer": await identity(ctx, p.prescriber_user_id),
        "source": p.source,
        "status": p.status,
        "items": values,
    }


async def event_detail(ctx, event):
    return {
        "event": row(event),
        "items": [
            row(i)
            for i in await ctx.session.scalars(
                select(m.DispensingItem)
                .where(m.DispensingItem.event_id == event.id)
                .order_by(m.DispensingItem.id)
            )
        ],
    }


async def dispense(ctx, data):
    share, p = await authorized_share(ctx, data["share_id"], data["organization_id"], True)
    ids = [i["prescription_item_id"] for i in data["items"]]
    require(
        len(ids) == len(set(ids)) and 1 <= len(ids) <= 100,
        "Provide unique medicine rows.",
        422,
        "VALIDATION_ERROR",
    )
    items = list(
        await ctx.session.scalars(
            select(m.PrescriptionItem)
            .where(m.PrescriptionItem.prescription_id == p.id, m.PrescriptionItem.id.in_(ids))
            .order_by(m.PrescriptionItem.id)
            .with_for_update()
        )
    )
    require(
        len(items) == len(ids),
        "A medicine does not belong to this prescription.",
        422,
        "VALIDATION_ERROR",
    )
    by_id = {i.id: i for i in items}
    for requested in data["items"]:
        item = by_id[requested["prescription_item_id"]]
        net = await net_dispensed(ctx, item.id)
        require(
            item.quantity is not None and requested["quantity_unit"] == item.quantity_unit,
            "Quantity unit does not match.",
            422,
            "VALIDATION_ERROR",
        )
        require(
            0 < requested["quantity"] <= item.quantity - net,
            "The requested amount exceeds the remaining quantity.",
            409,
            "OVERFILL",
        )
    event = await add(
        ctx,
        m.DispensingEvent,
        prescription_id=p.id,
        pharmacist_user_id=ctx.user.id,
        organization_id=data["organization_id"],
        share_id=share.id,
        notes=data.get("notes"),
        request_key=str(uuid4()),
    )
    for requested in data["items"]:
        await add(ctx, m.DispensingItem, event_id=event.id, **requested)
    return await event_detail(ctx, event)


async def own_dispensing(ctx, data, **filters):
    await professional(ctx, "pharmacist")
    result = await page(
        ctx,
        m.DispensingEvent,
        select(m.DispensingEvent).where(m.DispensingEvent.pharmacist_user_id == ctx.user.id),
        filters,
    )
    values = []
    for event in result["items"]:
        await membership(ctx, event["organization_id"], "pharmacist")
        detail = await event_detail(ctx, await get(ctx, m.DispensingEvent, event["id"]))
        values.append(
            {
                "id": event["id"],
                "prescription_reference": event["prescription_id"],
                "organization_id": event["organization_id"],
                "dispensed_at": event["dispensed_at"],
                "reversal_of_id": event["reversal_of_id"],
                "items": detail["items"],
            }
        )
    result["items"] = values
    return result


async def patient_dispensing(ctx, data, patient_id, **filters):
    ctx.own(patient_id)
    result = await page(
        ctx,
        m.DispensingEvent,
        select(m.DispensingEvent)
        .join(m.Prescription)
        .where(m.Prescription.patient_user_id == patient_id),
        filters,
    )
    result["items"] = [
        await event_detail(ctx, await get(ctx, m.DispensingEvent, v["id"])) for v in result["items"]
    ]
    return result


async def reverse_dispensing(ctx, data, event_id):
    original = await get(ctx, m.DispensingEvent, event_id, True)
    require(original.pharmacist_user_id == ctx.user.id and original.reversal_of_id is None)
    await membership(ctx, original.organization_id, "pharmacist")
    await get(ctx, m.Prescription, original.prescription_id, True)
    require(
        await ctx.session.scalar(
            select(m.DispensingEvent.id).where(m.DispensingEvent.reversal_of_id == original.id)
        )
        is None,
        "This event has already been reversed.",
        409,
        "CONFLICT",
    )
    event = await add(
        ctx,
        m.DispensingEvent,
        prescription_id=original.prescription_id,
        pharmacist_user_id=ctx.user.id,
        organization_id=original.organization_id,
        share_id=original.share_id,
        reversal_of_id=original.id,
        reason=data["reason"],
        request_key=str(uuid4()),
    )
    for item in await ctx.session.scalars(
        select(m.DispensingItem).where(m.DispensingItem.event_id == original.id)
    ):
        await get(ctx, m.PrescriptionItem, item.prescription_item_id, True)
        await add(
            ctx,
            m.DispensingItem,
            event_id=event.id,
            prescription_item_id=item.prescription_item_id,
            quantity=item.quantity,
            quantity_unit=item.quantity_unit,
        )
    return await event_detail(ctx, event)
