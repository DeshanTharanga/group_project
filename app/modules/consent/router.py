"""Thin async HTTP routes. Domain services own permissions and state transitions."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from app.core.security import Context, context
from app.modules.consent import schemas as s
from app.modules.consent import service
from app.services.common import invoke

router = APIRouter()


@router.get("/me/doctor-qr", tags=["Consent"], status_code=200, response_model=s.DoctorQrResponse)
async def doctor_qr(request: Request, ctx: Annotated[Context, Depends(context)]):
    result = await invoke(
        ctx,
        "doctor_qr",
        service.doctor_qr,
        None,
        params={},
        response_model=s.DoctorQrResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/doctor-qr/resolve", tags=["Consent"], status_code=200, response_model=s.ResolveDoctorResponse
)
async def resolve_doctor(
    request: Request, ctx: Annotated[Context, Depends(context)], data: s.ResolveDoctorInput
):
    result = await invoke(
        ctx,
        "resolve_doctor",
        service.resolve_doctor,
        data.model_dump(exclude_unset=True),
        params={},
        response_model=s.ResolveDoctorResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/access-grants", tags=["Consent"], status_code=201, response_model=s.CreateGrantResponse
)
async def create_grant(
    request: Request, ctx: Annotated[Context, Depends(context)], data: s.CreateGrantInput
):
    result = await invoke(
        ctx,
        "create_grant",
        service.create_grant,
        data.model_dump(exclude_unset=True),
        params={},
        response_model=s.CreateGrantResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.get(
    "/me/access-grants", tags=["Consent"], status_code=200, response_model=s.OwnGrantsResponse
)
async def own_grants(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
    status: Annotated[str | None, Query(alias="status", max_length=200)] = None,
):
    result = await invoke(
        ctx,
        "own_grants",
        service.own_grants,
        None,
        params={"page": page, "page_size": page_size, "status": status},
        response_model=s.OwnGrantsResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/access-grants/{grant_id}/revoke",
    tags=["Consent"],
    status_code=201,
    response_model=s.RevokeGrantResponse,
)
async def revoke_grant(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    grant_id: UUID,
    data: s.RevokeGrantInput,
):
    result = await invoke(
        ctx,
        "revoke_grant",
        service.revoke_grant,
        data.model_dump(exclude_unset=True),
        params={"grant_id": grant_id},
        response_model=s.RevokeGrantResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.get(
    "/me/patient-queue", tags=["Consent"], status_code=200, response_model=s.PatientQueueResponse
)
async def patient_queue(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
):
    result = await invoke(
        ctx,
        "patient_queue",
        service.patient_queue,
        None,
        params={"page": page, "page_size": page_size},
        response_model=s.PatientQueueResponse,
        status=200,
        idempotent=False,
    )
    return result
