"""Thin async HTTP routes. Domain services own permissions and state transitions."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from app.core.security import Context, context
from app.modules.organizations import schemas as s
from app.modules.organizations import service
from app.services.common import invoke

router = APIRouter()


@router.get(
    "/organizations",
    tags=["Organizations"],
    status_code=200,
    response_model=s.ListOrganizationsResponse,
)
async def list_organizations(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
    type: Annotated[str | None, Query(alias="type", max_length=200)] = None,
    q: Annotated[str | None, Query(alias="q", max_length=200)] = None,
):
    result = await invoke(
        ctx,
        "list_organizations",
        service.list_organizations,
        None,
        params={"page": page, "page_size": page_size, "type": type, "q": q},
        response_model=s.ListOrganizationsResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/organizations",
    tags=["Organizations"],
    status_code=201,
    response_model=s.CreateOrganizationResponse,
)
async def create_organization(
    request: Request, ctx: Annotated[Context, Depends(context)], data: s.CreateOrganizationInput
):
    result = await invoke(
        ctx,
        "create_organization",
        service.create_organization,
        data.model_dump(exclude_unset=True),
        params={},
        response_model=s.CreateOrganizationResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.post(
    "/me/memberships",
    tags=["Organizations"],
    status_code=201,
    response_model=s.RequestMembershipResponse,
)
async def request_membership(
    request: Request, ctx: Annotated[Context, Depends(context)], data: s.RequestMembershipInput
):
    result = await invoke(
        ctx,
        "request_membership",
        service.request_membership,
        data.model_dump(exclude_unset=True),
        params={},
        response_model=s.RequestMembershipResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.post(
    "/admin/organizations/{organization_id}/decision",
    tags=["Organizations"],
    status_code=201,
    response_model=s.DecideOrganizationResponse,
)
async def decide_organization(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    organization_id: UUID,
    data: s.DecideOrganizationInput,
):
    result = await invoke(
        ctx,
        "decide_organization",
        service.decide_organization,
        data.model_dump(exclude_unset=True),
        params={"organization_id": organization_id},
        response_model=s.DecideOrganizationResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.get(
    "/admin/organizations",
    tags=["Organizations"],
    status_code=200,
    response_model=s.AdminOrganizationsResponse,
)
async def admin_organizations(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
    status: Annotated[str | None, Query(alias="status", max_length=200)] = None,
    type: Annotated[str | None, Query(alias="type", max_length=200)] = None,
):
    result = await invoke(
        ctx,
        "admin_organizations",
        service.admin_organizations,
        None,
        params={"page": page, "page_size": page_size, "status": status, "type": type},
        response_model=s.AdminOrganizationsResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.get(
    "/admin/memberships",
    tags=["Organizations"],
    status_code=200,
    response_model=s.AdminMembershipsResponse,
)
async def admin_memberships(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
    organization_id: Annotated[UUID | None, Query(alias="organization_id")] = None,
    status: Annotated[str | None, Query(alias="status", max_length=200)] = None,
):
    result = await invoke(
        ctx,
        "admin_memberships",
        service.admin_memberships,
        None,
        params={
            "page": page,
            "page_size": page_size,
            "organization_id": organization_id,
            "status": status,
        },
        response_model=s.AdminMembershipsResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/admin/memberships/{membership_id}/decision",
    tags=["Organizations"],
    status_code=201,
    response_model=s.DecideMembershipResponse,
)
async def decide_membership(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    membership_id: UUID,
    data: s.DecideMembershipInput,
):
    result = await invoke(
        ctx,
        "decide_membership",
        service.decide_membership,
        data.model_dump(exclude_unset=True),
        params={"membership_id": membership_id},
        response_model=s.DecideMembershipResponse,
        status=201,
        idempotent=False,
    )
    return result
