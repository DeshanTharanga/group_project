"""Thin async HTTP routes. Domain services own permissions and state transitions."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from app.core.security import Context, context
from app.modules.verification import schemas as s
from app.modules.verification import service
from app.services.common import invoke

router = APIRouter()


@router.post(
    "/verification-applications",
    tags=["Verification"],
    status_code=201,
    response_model=s.SubmitVerificationResponse,
)
async def submit_verification(
    request: Request, ctx: Annotated[Context, Depends(context)], data: s.SubmitVerificationInput
):
    result = await invoke(
        ctx,
        "submit_verification",
        service.submit_verification,
        data.model_dump(exclude_unset=True),
        params={},
        response_model=s.SubmitVerificationResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.get(
    "/me/verification-applications",
    tags=["Verification"],
    status_code=200,
    response_model=s.OwnVerificationsResponse,
)
async def own_verifications(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
):
    result = await invoke(
        ctx,
        "own_verifications",
        service.own_verifications,
        None,
        params={"page": page, "page_size": page_size},
        response_model=s.OwnVerificationsResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.get(
    "/admin/verification-applications",
    tags=["Verification"],
    status_code=200,
    response_model=s.AdminVerificationsResponse,
)
async def admin_verifications(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
    status: Annotated[str | None, Query(alias="status", max_length=200)] = None,
    role: Annotated[str | None, Query(alias="role", max_length=200)] = None,
):
    result = await invoke(
        ctx,
        "admin_verifications",
        service.admin_verifications,
        None,
        params={"page": page, "page_size": page_size, "status": status, "role": role},
        response_model=s.AdminVerificationsResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.get(
    "/admin/verification-applications/{application_id}",
    tags=["Verification"],
    status_code=200,
    response_model=s.VerificationDetailResponse,
)
async def verification_detail(
    request: Request, ctx: Annotated[Context, Depends(context)], application_id: UUID
):
    result = await invoke(
        ctx,
        "verification_detail",
        service.verification_detail,
        None,
        params={"application_id": application_id},
        response_model=s.VerificationDetailResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/admin/verification-applications/{application_id}/decision",
    tags=["Verification"],
    status_code=201,
    response_model=s.DecideVerificationResponse,
)
async def decide_verification(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    application_id: UUID,
    data: s.DecideVerificationInput,
):
    result = await invoke(
        ctx,
        "decide_verification",
        service.decide_verification,
        data.model_dump(exclude_unset=True),
        params={"application_id": application_id},
        response_model=s.DecideVerificationResponse,
        status=201,
        idempotent=False,
    )
    return result
