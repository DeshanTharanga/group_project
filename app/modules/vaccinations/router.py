"""Thin async HTTP routes. Domain services own permissions and state transitions."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from pydantic import AwareDatetime

from app.core.security import Context, context
from app.modules.vaccinations import schemas as s
from app.modules.vaccinations import service
from app.services.common import invoke

router = APIRouter()


@router.get(
    "/patients/{patient_id}/vaccinations",
    tags=["Vaccinations"],
    status_code=200,
    response_model=s.ListVaccinationsResponse,
)
async def list_vaccinations(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    patient_id: UUID,
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
    from_: Annotated[AwareDatetime | None, Query(alias="from")] = None,
    to: Annotated[AwareDatetime | None, Query(alias="to")] = None,
):
    result = await invoke(
        ctx,
        "list_vaccinations",
        service.list_vaccinations,
        None,
        params={
            "patient_id": patient_id,
            "page": page,
            "page_size": page_size,
            "from": from_,
            "to": to,
        },
        response_model=s.ListVaccinationsResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/patients/{patient_id}/vaccinations",
    tags=["Vaccinations"],
    status_code=201,
    response_model=s.CreateVaccinationResponse,
)
async def create_vaccination(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    patient_id: UUID,
    data: s.CreateVaccinationInput,
):
    result = await invoke(
        ctx,
        "create_vaccination",
        service.create_vaccination,
        data.model_dump(exclude_unset=True),
        params={"patient_id": patient_id},
        response_model=s.CreateVaccinationResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.post(
    "/vaccinations/{record_id}/versions",
    tags=["Vaccinations"],
    status_code=201,
    response_model=s.ReplaceVaccinationResponse,
)
async def replace_vaccination(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    record_id: UUID,
    data: s.ReplaceVaccinationInput,
):
    result = await invoke(
        ctx,
        "replace_vaccination",
        service.replace_vaccination,
        data.model_dump(exclude_unset=True),
        params={"record_id": record_id},
        response_model=s.ReplaceVaccinationResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.get(
    "/vaccinations/{record_id}/history",
    tags=["Vaccinations"],
    status_code=200,
    response_model=s.VaccinationHistoryResponse,
)
async def vaccination_history(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    record_id: UUID,
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
):
    result = await invoke(
        ctx,
        "vaccination_history",
        service.vaccination_history,
        None,
        params={"record_id": record_id, "page": page, "page_size": page_size},
        response_model=s.VaccinationHistoryResponse,
        status=200,
        idempotent=False,
    )
    return result
