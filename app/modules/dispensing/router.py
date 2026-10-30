"""Thin async HTTP routes. Domain services own permissions and state transitions."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from app.core.security import Context, context
from app.modules.dispensing import schemas as s
from app.modules.dispensing import service
from app.services.common import invoke

router = APIRouter()


@router.post(
    "/prescription-shares", tags=["Pharmacy"], status_code=201, response_model=s.CreateShareResponse
)
async def create_share(
    request: Request, ctx: Annotated[Context, Depends(context)], data: s.CreateShareInput
):
    result = await invoke(
        ctx,
        "create_share",
        service.create_share,
        data.model_dump(exclude_unset=True),
        params={},
        response_model=s.CreateShareResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.get(
    "/me/prescription-shares",
    tags=["Pharmacy"],
    status_code=200,
    response_model=s.OwnSharesResponse,
)
async def own_shares(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
):
    result = await invoke(
        ctx,
        "own_shares",
        service.own_shares,
        None,
        params={"page": page, "page_size": page_size},
        response_model=s.OwnSharesResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/prescription-shares/claim",
    tags=["Pharmacy"],
    status_code=200,
    response_model=s.ClaimShareResponse,
)
async def claim_share(
    request: Request, ctx: Annotated[Context, Depends(context)], data: s.ClaimShareInput
):
    result = await invoke(
        ctx,
        "claim_share",
        service.claim_share,
        data.model_dump(exclude_unset=True),
        params={},
        response_model=s.ClaimShareResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.get(
    "/prescription-shares/{share_id}",
    tags=["Pharmacy"],
    status_code=200,
    response_model=s.ShareDetailResponse,
)
async def share_detail(request: Request, ctx: Annotated[Context, Depends(context)], share_id: UUID):
    result = await invoke(
        ctx,
        "share_detail",
        service.share_detail,
        None,
        params={"share_id": share_id},
        response_model=s.ShareDetailResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/prescription-shares/{share_id}/confirm",
    tags=["Pharmacy"],
    status_code=200,
    response_model=s.ConfirmShareResponse,
)
async def confirm_share(
    request: Request, ctx: Annotated[Context, Depends(context)], share_id: UUID
):
    result = await invoke(
        ctx,
        "confirm_share",
        service.confirm_share,
        None,
        params={"share_id": share_id},
        response_model=s.ConfirmShareResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/prescription-shares/{share_id}/revoke",
    tags=["Pharmacy"],
    status_code=201,
    response_model=s.RevokeShareResponse,
)
async def revoke_share(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    share_id: UUID,
    data: s.RevokeShareInput,
):
    result = await invoke(
        ctx,
        "revoke_share",
        service.revoke_share,
        data.model_dump(exclude_unset=True),
        params={"share_id": share_id},
        response_model=s.RevokeShareResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.get(
    "/prescription-shares/{share_id}/prescription",
    tags=["Pharmacy"],
    status_code=200,
    response_model=s.SharedPrescriptionResponse,
)
async def shared_prescription(
    request: Request, ctx: Annotated[Context, Depends(context)], share_id: UUID
):
    result = await invoke(
        ctx,
        "shared_prescription",
        service.shared_prescription,
        None,
        params={"share_id": share_id},
        response_model=s.SharedPrescriptionResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/dispensing-events", tags=["Pharmacy"], status_code=201, response_model=s.DispenseResponse
)
async def dispense(
    request: Request, ctx: Annotated[Context, Depends(context)], data: s.DispenseInput
):
    result = await invoke(
        ctx,
        "dispense",
        service.dispense,
        data.model_dump(exclude_unset=True),
        params={},
        response_model=s.DispenseResponse,
        status=201,
        idempotent=True,
    )
    return result


@router.get(
    "/me/dispensing-events",
    tags=["Pharmacy"],
    status_code=200,
    response_model=s.OwnDispensingResponse,
)
async def own_dispensing(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
):
    result = await invoke(
        ctx,
        "own_dispensing",
        service.own_dispensing,
        None,
        params={"page": page, "page_size": page_size},
        response_model=s.OwnDispensingResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.get(
    "/patients/{patient_id}/dispensing-events",
    tags=["Pharmacy"],
    status_code=200,
    response_model=s.PatientDispensingResponse,
)
async def patient_dispensing(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    patient_id: UUID,
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
):
    result = await invoke(
        ctx,
        "patient_dispensing",
        service.patient_dispensing,
        None,
        params={"patient_id": patient_id, "page": page, "page_size": page_size},
        response_model=s.PatientDispensingResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/dispensing-events/{event_id}/reversal",
    tags=["Pharmacy"],
    status_code=201,
    response_model=s.ReverseDispensingResponse,
)
async def reverse_dispensing(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    event_id: UUID,
    data: s.ReverseDispensingInput,
):
    result = await invoke(
        ctx,
        "reverse_dispensing",
        service.reverse_dispensing,
        data.model_dump(exclude_unset=True),
        params={"event_id": event_id},
        response_model=s.ReverseDispensingResponse,
        status=201,
        idempotent=True,
    )
    return result
