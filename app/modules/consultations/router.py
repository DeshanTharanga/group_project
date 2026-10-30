"""Thin async HTTP routes. Domain services own permissions and state transitions."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from app.core.security import Context, context
from app.modules.consultations import schemas as s
from app.modules.consultations import service
from app.services.common import invoke

router = APIRouter()


@router.post(
    "/consultations",
    tags=["Consultations"],
    status_code=201,
    response_model=s.StartConsultationResponse,
)
async def start_consultation(
    request: Request, ctx: Annotated[Context, Depends(context)], data: s.StartConsultationInput
):
    result = await invoke(
        ctx,
        "start_consultation",
        service.start_consultation,
        data.model_dump(exclude_unset=True),
        params={},
        response_model=s.StartConsultationResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.get(
    "/patients/{patient_id}/consultations",
    tags=["Consultations"],
    status_code=200,
    response_model=s.ListConsultationsResponse,
)
async def list_consultations(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    patient_id: UUID,
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
):
    result = await invoke(
        ctx,
        "list_consultations",
        service.list_consultations,
        None,
        params={"patient_id": patient_id, "page": page, "page_size": page_size},
        response_model=s.ListConsultationsResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/consultations/{consultation_id}/end",
    tags=["Consultations"],
    status_code=201,
    response_model=s.EndConsultationResponse,
)
async def end_consultation(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    consultation_id: UUID,
    data: s.EndConsultationInput,
):
    result = await invoke(
        ctx,
        "end_consultation",
        service.end_consultation,
        data.model_dump(exclude_unset=True),
        params={"consultation_id": consultation_id},
        response_model=s.EndConsultationResponse,
        status=201,
        idempotent=False,
    )
    return result
