"""Thin async HTTP routes. Domain services own permissions and state transitions."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from pydantic import AwareDatetime

from app.core.security import Context, context
from app.modules.clinical_records import schemas as s
from app.modules.clinical_records import service
from app.services.common import invoke

router = APIRouter()


@router.get(
    "/patients/{patient_id}/clinical-records",
    tags=["Clinical records"],
    status_code=200,
    response_model=s.ListClinicalRecordsResponse,
)
async def list_clinical_records(
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
        "list_clinical_records",
        service.list_clinical_records,
        None,
        params={
            "patient_id": patient_id,
            "page": page,
            "page_size": page_size,
            "type": type,
            "from": from_,
            "to": to,
        },
        response_model=s.ListClinicalRecordsResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/patients/{patient_id}/clinical-records",
    tags=["Clinical records"],
    status_code=201,
    response_model=s.CreateClinicalRecordResponse,
)
async def create_clinical_record(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    patient_id: UUID,
    data: s.CreateClinicalRecordInput,
):
    result = await invoke(
        ctx,
        "create_clinical_record",
        service.create_clinical_record,
        data.model_dump(exclude_unset=True),
        params={"patient_id": patient_id},
        response_model=s.CreateClinicalRecordResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.post(
    "/clinical-records/{record_id}/versions",
    tags=["Clinical records"],
    status_code=201,
    response_model=s.ReplaceClinicalRecordResponse,
)
async def replace_clinical_record(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    record_id: UUID,
    data: s.ReplaceClinicalRecordInput,
):
    result = await invoke(
        ctx,
        "replace_clinical_record",
        service.replace_clinical_record,
        data.model_dump(exclude_unset=True),
        params={"record_id": record_id},
        response_model=s.ReplaceClinicalRecordResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.get(
    "/clinical-records/{record_id}/history",
    tags=["Clinical records"],
    status_code=200,
    response_model=s.ClinicalHistoryResponse,
)
async def clinical_history(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    record_id: UUID,
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
):
    result = await invoke(
        ctx,
        "clinical_history",
        service.clinical_history,
        None,
        params={"record_id": record_id, "page": page, "page_size": page_size},
        response_model=s.ClinicalHistoryResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.get(
    "/clinical-records/{record_id}",
    tags=["Clinical records"],
    status_code=200,
    response_model=s.ClinicalDetailResponse,
)
async def clinical_detail(
    request: Request, ctx: Annotated[Context, Depends(context)], record_id: UUID
):
    result = await invoke(
        ctx,
        "clinical_detail",
        service.clinical_detail,
        None,
        params={"record_id": record_id},
        response_model=s.ClinicalDetailResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/clinical-records/{record_id}/correction-requests",
    tags=["Clinical records"],
    status_code=201,
    response_model=s.RequestCorrectionResponse,
)
async def request_correction(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    record_id: UUID,
    data: s.RequestCorrectionInput,
):
    result = await invoke(
        ctx,
        "request_correction",
        service.request_correction,
        data.model_dump(exclude_unset=True),
        params={"record_id": record_id},
        response_model=s.RequestCorrectionResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.get(
    "/clinical-records/{record_id}/correction-requests",
    tags=["Clinical records"],
    status_code=200,
    response_model=s.ListCorrectionsResponse,
)
async def list_corrections(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    record_id: UUID,
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
):
    result = await invoke(
        ctx,
        "list_corrections",
        service.list_corrections,
        None,
        params={"record_id": record_id, "page": page, "page_size": page_size},
        response_model=s.ListCorrectionsResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/correction-requests/{correction_id}/decision",
    tags=["Clinical records"],
    status_code=201,
    response_model=s.DecideCorrectionResponse,
)
async def decide_correction(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    correction_id: UUID,
    data: s.DecideCorrectionInput,
):
    result = await invoke(
        ctx,
        "decide_correction",
        service.decide_correction,
        data.model_dump(exclude_unset=True),
        params={"correction_id": correction_id},
        response_model=s.DecideCorrectionResponse,
        status=201,
        idempotent=False,
    )
    return result
