"""Thin async HTTP routes. Domain services own permissions and state transitions."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from pydantic import AwareDatetime

from app.core.security import Context, context
from app.modules.measurements import schemas as s
from app.modules.measurements import service
from app.services.common import invoke

router = APIRouter()


@router.get(
    "/patients/{patient_id}/measurements",
    tags=["Measurements"],
    status_code=200,
    response_model=s.ListMeasurementsResponse,
)
async def list_measurements(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    patient_id: UUID,
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
    type: Annotated[str | None, Query(alias="type", max_length=200)] = None,
    from_: Annotated[AwareDatetime | None, Query(alias="from")] = None,
    to: Annotated[AwareDatetime | None, Query(alias="to")] = None,
):
    result = await invoke(
        ctx,
        "list_measurements",
        service.list_measurements,
        None,
        params={
            "patient_id": patient_id,
            "page": page,
            "page_size": page_size,
            "type": type,
            "from": from_,
            "to": to,
        },
        response_model=s.ListMeasurementsResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/patients/{patient_id}/measurements",
    tags=["Measurements"],
    status_code=201,
    response_model=s.CreateMeasurementResponse,
)
async def create_measurement(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    patient_id: UUID,
    data: s.CreateMeasurementInput,
):
    result = await invoke(
        ctx,
        "create_measurement",
        service.create_measurement,
        data.model_dump(exclude_unset=True),
        params={"patient_id": patient_id},
        response_model=s.CreateMeasurementResponse,
        status=201,
        idempotent=False,
    )
    return result
