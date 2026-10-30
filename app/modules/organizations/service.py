"""Organization registration and membership review remain separate from clinical access."""

from sqlalchemy import select

from app.core.errors import require
from app.database import models as m
from app.services.common import add, get, now, page, row


async def list_organizations(ctx, data, **filters):
    query = select(m.Organization).where(m.Organization.status == "active")
    if filters.get("q"):
        query = query.where(m.Organization.name.ilike("%" + filters["q"] + "%"))
    return await page(ctx, m.Organization, query, filters)


async def create_organization(ctx, data):
    # All humans may submit applications; only a super admin can activate them.
    return row(await add(ctx, m.Organization, **data, status="pending"))


async def request_membership(ctx, data):
    require(data["role"] in ctx.roles)
    profile = await get(ctx, m.ProfessionalProfile, ctx.user.id)
    require(profile.role == data["role"])
    org = await get(ctx, m.Organization, data["organization_id"])
    require(org.status == "active")
    require(data["role"] != "pharmacist" or org.type == "pharmacy")
    require(data["role"] != "lab_staff" or org.type == "laboratory")
    member = await ctx.session.scalar(
        select(m.OrganizationMembership).where(
            m.OrganizationMembership.organization_id == org.id,
            m.OrganizationMembership.user_id == ctx.user.id,
            m.OrganizationMembership.role == data["role"],
        )
    )
    if member:
        return row(member)
    return row(
        await add(ctx, m.OrganizationMembership, user_id=ctx.user.id, **data, status="pending")
    )


async def decide_organization(ctx, data, organization_id):
    ctx.admin(super_only=True)
    org = await get(ctx, m.Organization, organization_id, lock=True)
    org.status = data["status"]
    await ctx.session.flush()
    return row(org)


async def admin_organizations(ctx, data, **filters):
    ctx.admin()
    return await page(ctx, m.Organization, filters=filters)


async def admin_memberships(ctx, data, **filters):
    ctx.admin()
    return await page(ctx, m.OrganizationMembership, filters=filters)


async def decide_membership(ctx, data, membership_id):
    ctx.admin()
    member = await get(ctx, m.OrganizationMembership, membership_id, lock=True)
    require(member.user_id != ctx.user.id, "You cannot review your own membership.")
    profile = await get(ctx, m.ProfessionalProfile, member.user_id)
    org = await get(ctx, m.Organization, member.organization_id)
    if data["status"] == "approved":
        require(
            profile.verification_status == "approved"
            and profile.role == member.role
            and org.status == "active"
        )
    member.status = data["status"]
    member.verified_at = now() if member.status == "approved" else None
    await ctx.session.flush()
    return row(member)
