"""Identity reconciliation never grants professional approval or privileged roles."""

import secrets
from datetime import date

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.core.errors import require
from app.database import models as m
from app.services.common import add, row


async def account(ctx):
    user = ctx.user
    roles = list(
        await ctx.session.scalars(
            select(m.Role.code)
            .join(m.UserRole, m.UserRole.role_id == m.Role.id)
            .where(m.UserRole.user_id == user.id)
        )
    )
    memberships = list(
        await ctx.session.scalars(
            select(m.OrganizationMembership)
            .where(m.OrganizationMembership.user_id == user.id)
            .order_by(m.OrganizationMembership.created_at, m.OrganizationMembership.id)
        )
    )
    return {
        "user": row(user),
        "roles": roles,
        "patient_profile": row(await ctx.session.get(m.PatientProfile, user.id)),
        "professional_profile": row(await ctx.session.get(m.ProfessionalProfile, user.id)),
        "memberships": [row(v) for v in memberships],
    }


async def onboard(ctx, data):
    statement = insert(m.User).values(
        firebase_uid=ctx.identity["uid"],
        email=ctx.identity.get("email"),
        display_name=data["display_name"],
        phone=data.get("phone"),
        status="active",
    )
    # Preserve existing status and user-managed contact fields during reconciliation.
    await ctx.session.execute(statement.on_conflict_do_nothing(index_elements=["firebase_uid"]))
    ctx.user = await ctx.session.scalar(
        select(m.User).where(m.User.firebase_uid == ctx.identity["uid"]).with_for_update()
    )
    require(ctx.user.status == "active", "This account is not active.")
    role = await ctx.session.scalar(select(m.Role).where(m.Role.code == data["requested_role"]))
    require(role is not None, "Roles have not been initialized.", 503, "SETUP_REQUIRED")
    await ctx.session.execute(
        insert(m.UserRole).values(user_id=ctx.user.id, role_id=role.id).on_conflict_do_nothing()
    )
    if data["requested_role"] != "patient":
        existing = await ctx.session.get(m.ProfessionalProfile, ctx.user.id)
        require(
            existing is None or existing.role == data["requested_role"],
            "Update the professional profile to change its role.",
            409,
            "CONFLICT",
        )
        if existing is None:
            await add(
                ctx,
                m.ProfessionalProfile,
                user_id=ctx.user.id,
                role=data["requested_role"],
                doctor_reference=secrets.token_urlsafe(32)
                if data["requested_role"] == "doctor"
                else None,
            )
    return await account(ctx)


async def me(ctx, data):
    return await account(ctx)


async def update_me(ctx, data):
    for key in ("display_name", "phone"):
        if key in data:
            setattr(ctx.user, key, data[key])
    await ctx.session.flush()
    return await account(ctx)


async def update_patient_profile(ctx, data):
    require("patient" in ctx.roles)
    profile = await ctx.session.get(m.PatientProfile, ctx.user.id)
    if data.get("date_of_birth"):
        require(
            data["date_of_birth"] <= date.today(),
            "Birth date cannot be in the future.",
            422,
            "VALIDATION_ERROR",
        )
    if profile is None:
        require(
            data.get("date_of_birth") is not None and data.get("sex") is not None,
            "Birth date and sex are required to complete a patient profile.",
            422,
            "PROFILE_INCOMPLETE",
        )
        profile = await add(ctx, m.PatientProfile, user_id=ctx.user.id, **data)
    else:
        for key, value in data.items():
            if key == "notification_preferences":
                value = {**profile.notification_preferences, **value}
            setattr(profile, key, value)
        await ctx.session.flush()
    return row(profile)


async def update_professional_profile(ctx, data):
    role = await ctx.session.scalar(select(m.Role).where(m.Role.code == data["role"]))
    require(role is not None)
    await ctx.session.execute(
        insert(m.UserRole).values(user_id=ctx.user.id, role_id=role.id).on_conflict_do_nothing()
    )
    profile = await ctx.session.get(m.ProfessionalProfile, ctx.user.id)
    if profile is None:
        profile = await add(
            ctx,
            m.ProfessionalProfile,
            user_id=ctx.user.id,
            role=data["role"],
            doctor_reference=secrets.token_urlsafe(32) if data["role"] == "doctor" else None,
        )
    changed = profile.role != data["role"] or profile.registration_number != data.get(
        "registration_number"
    )
    if changed:
        profile.verification_status = "not_submitted"
        profile.doctor_reference = secrets.token_urlsafe(32) if data["role"] == "doctor" else None
        for member in await ctx.session.scalars(
            select(m.OrganizationMembership).where(m.OrganizationMembership.user_id == ctx.user.id)
        ):
            member.status, member.verified_at = "suspended", None
    for key, value in data.items():
        setattr(profile, key, value)
    await ctx.session.flush()
    return row(profile)
