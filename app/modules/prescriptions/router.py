"""Thin async HTTP routes. Domain services own permissions and state transitions."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Response

from app.core.security import Context, context
from app.modules.prescriptions import schemas as s
from app.modules.prescriptions import service
from app.services.common import invoke

router = APIRouter()


@router.get(
    "/medicines", tags=["Medicines"], status_code=200, response_model=s.ListMedicinesResponse
)
async def list_medicines(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
    q: Annotated[str | None, Query(alias="q", max_length=200)] = None,
):
    result = await invoke(
        ctx,
        "list_medicines",
        service.list_medicines,
        None,
        params={"page": page, "page_size": page_size, "q": q},
        response_model=s.ListMedicinesResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/admin/medicines", tags=["Medicines"], status_code=201, response_model=s.CreateMedicineResponse
)
async def create_medicine(
    request: Request, ctx: Annotated[Context, Depends(context)], data: s.CreateMedicineInput
):
    result = await invoke(
        ctx,
        "create_medicine",
        service.create_medicine,
        data.model_dump(exclude_unset=True),
        params={},
        response_model=s.CreateMedicineResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.get(
    "/patients/{patient_id}/prescriptions",
    tags=["Prescriptions"],
    status_code=200,
    response_model=s.ListPrescriptionsResponse,
)
async def list_prescriptions(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    patient_id: UUID,
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
    status: Annotated[str | None, Query(alias="status", max_length=200)] = None,
    source: Annotated[str | None, Query(alias="source", max_length=200)] = None,
):
    result = await invoke(
        ctx,
        "list_prescriptions",
        service.list_prescriptions,
        None,
        params={
            "patient_id": patient_id,
            "page": page,
            "page_size": page_size,
            "status": status,
            "source": source,
        },
        response_model=s.ListPrescriptionsResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/patients/{patient_id}/prescriptions",
    tags=["Prescriptions"],
    status_code=201,
    response_model=s.CreatePrescriptionResponse,
)
async def create_prescription(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    patient_id: UUID,
    data: s.CreatePrescriptionInput,
):
    result = await invoke(
        ctx,
        "create_prescription",
        service.create_prescription,
        data.model_dump(exclude_unset=True),
        params={"patient_id": patient_id},
        response_model=s.CreatePrescriptionResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.get(
    "/prescriptions/{prescription_id}",
    tags=["Prescriptions"],
    status_code=200,
    response_model=s.PrescriptionDetailResponse,
)
async def prescription_detail(
    request: Request, ctx: Annotated[Context, Depends(context)], prescription_id: UUID
):
    result = await invoke(
        ctx,
        "prescription_detail",
        service.prescription_detail,
        None,
        params={"prescription_id": prescription_id},
        response_model=s.PrescriptionDetailResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.put(
    "/prescriptions/{prescription_id}/draft",
    tags=["Prescriptions"],
    status_code=200,
    response_model=s.UpdateDraftResponse,
)
async def update_draft(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    prescription_id: UUID,
    data: s.UpdateDraftInput,
):
    result = await invoke(
        ctx,
        "update_draft",
        service.update_draft,
        data.model_dump(exclude_unset=True),
        params={"prescription_id": prescription_id},
        response_model=s.UpdateDraftResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.delete("/prescriptions/{prescription_id}/draft", tags=["Prescriptions"], status_code=204)
async def delete_draft(
    request: Request, ctx: Annotated[Context, Depends(context)], prescription_id: UUID
):
    await invoke(
        ctx,
        "delete_draft",
        service.delete_draft,
        None,
        params={"prescription_id": prescription_id},
        response_model=None,
        status=204,
        idempotent=False,
    )
    return Response(status_code=204)


@router.post(
    "/prescriptions/{prescription_id}/confirm",
    tags=["Prescriptions"],
    status_code=200,
    response_model=s.ConfirmPrescriptionResponse,
)
async def confirm_prescription(
    request: Request, ctx: Annotated[Context, Depends(context)], prescription_id: UUID
):
    result = await invoke(
        ctx,
        "confirm_prescription",
        service.confirm_prescription,
        None,
        params={"prescription_id": prescription_id},
        response_model=s.ConfirmPrescriptionResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/prescriptions/{prescription_id}/issue",
    tags=["Prescriptions"],
    status_code=200,
    response_model=s.IssuePrescriptionResponse,
)
async def issue_prescription(
    request: Request, ctx: Annotated[Context, Depends(context)], prescription_id: UUID
):
    result = await invoke(
        ctx,
        "issue_prescription",
        service.issue_prescription,
        None,
        params={"prescription_id": prescription_id},
        response_model=s.IssuePrescriptionResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/prescriptions/{prescription_id}/reviews",
    tags=["Prescriptions"],
    status_code=201,
    response_model=s.ReviewPrescriptionResponse,
)
async def review_prescription(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    prescription_id: UUID,
    data: s.ReviewPrescriptionInput,
):
    result = await invoke(
        ctx,
        "review_prescription",
        service.review_prescription,
        data.model_dump(exclude_unset=True),
        params={"prescription_id": prescription_id},
        response_model=s.ReviewPrescriptionResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.post(
    "/prescriptions/{prescription_id}/versions",
    tags=["Prescriptions"],
    status_code=201,
    response_model=s.VersionPrescriptionResponse,
)
async def version_prescription(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    prescription_id: UUID,
    data: s.VersionPrescriptionInput,
):
    result = await invoke(
        ctx,
        "version_prescription",
        service.version_prescription,
        data.model_dump(exclude_unset=True),
        params={"prescription_id": prescription_id},
        response_model=s.VersionPrescriptionResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.post(
    "/prescriptions/{prescription_id}/renewals",
    tags=["Prescriptions"],
    status_code=201,
    response_model=s.RenewPrescriptionResponse,
)
async def renew_prescription(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    prescription_id: UUID,
    data: s.RenewPrescriptionInput,
):
    result = await invoke(
        ctx,
        "renew_prescription",
        service.renew_prescription,
        data.model_dump(exclude_unset=True),
        params={"prescription_id": prescription_id},
        response_model=s.RenewPrescriptionResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.post(
    "/prescriptions/{prescription_id}/reissues",
    tags=["Prescriptions"],
    status_code=201,
    response_model=s.ReissuePrescriptionResponse,
)
async def reissue_prescription(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    prescription_id: UUID,
    data: s.ReissuePrescriptionInput,
):
    result = await invoke(
        ctx,
        "reissue_prescription",
        service.reissue_prescription,
        data.model_dump(exclude_unset=True),
        params={"prescription_id": prescription_id},
        response_model=s.ReissuePrescriptionResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.post(
    "/prescriptions/{prescription_id}/cancel",
    tags=["Prescriptions"],
    status_code=201,
    response_model=s.CancelPrescriptionResponse,
)
async def cancel_prescription(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    prescription_id: UUID,
    data: s.CancelPrescriptionInput,
):
    result = await invoke(
        ctx,
        "cancel_prescription",
        service.cancel_prescription,
        data.model_dump(exclude_unset=True),
        params={"prescription_id": prescription_id},
        response_model=s.CancelPrescriptionResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.post(
    "/prescriptions/{prescription_id}/discontinue",
    tags=["Prescriptions"],
    status_code=201,
    response_model=s.DiscontinuePrescriptionResponse,
)
async def discontinue_prescription(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    prescription_id: UUID,
    data: s.DiscontinuePrescriptionInput,
):
    result = await invoke(
        ctx,
        "discontinue_prescription",
        service.discontinue_prescription,
        data.model_dump(exclude_unset=True),
        params={"prescription_id": prescription_id},
        response_model=s.DiscontinuePrescriptionResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.post(
    "/prescriptions/{prescription_id}/complete",
    tags=["Prescriptions"],
    status_code=201,
    response_model=s.CompletePrescriptionResponse,
)
async def complete_prescription(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    prescription_id: UUID,
    data: s.CompletePrescriptionInput,
):
    result = await invoke(
        ctx,
        "complete_prescription",
        service.complete_prescription,
        data.model_dump(exclude_unset=True),
        params={"prescription_id": prescription_id},
        response_model=s.CompletePrescriptionResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.get(
    "/prescriptions/{prescription_id}/history",
    tags=["Prescriptions"],
    status_code=200,
    response_model=s.PrescriptionHistoryResponse,
)
async def prescription_history(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    prescription_id: UUID,
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
):
    result = await invoke(
        ctx,
        "prescription_history",
        service.prescription_history,
        None,
        params={"prescription_id": prescription_id, "page": page, "page_size": page_size},
        response_model=s.PrescriptionHistoryResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.get("/prescriptions/{prescription_id}/pdf", tags=["Prescriptions"], status_code=200)
async def prescription_pdf(
    request: Request, ctx: Annotated[Context, Depends(context)], prescription_id: UUID
):
    result = await invoke(
        ctx,
        "prescription_pdf",
        service.prescription_pdf,
        None,
        params={"prescription_id": prescription_id},
        response_model=None,
        status=200,
        idempotent=False,
    )
    return result


@router.get(
    "/me/prescription-templates",
    tags=["Prescribing shortcuts"],
    status_code=200,
    response_model=s.ListTemplatesResponse,
)
async def list_templates(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
    template_type: Annotated[str | None, Query(alias="template_type", max_length=200)] = None,
    status: Annotated[str | None, Query(alias="status", max_length=200)] = None,
):
    result = await invoke(
        ctx,
        "list_templates",
        service.list_templates,
        None,
        params={
            "page": page,
            "page_size": page_size,
            "template_type": template_type,
            "status": status,
        },
        response_model=s.ListTemplatesResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/me/prescription-templates",
    tags=["Prescribing shortcuts"],
    status_code=201,
    response_model=s.CreateTemplateResponse,
)
async def create_template(
    request: Request, ctx: Annotated[Context, Depends(context)], data: s.CreateTemplateInput
):
    result = await invoke(
        ctx,
        "create_template",
        service.create_template,
        data.model_dump(exclude_unset=True),
        params={},
        response_model=s.CreateTemplateResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.patch(
    "/prescription-templates/{template_id}",
    tags=["Prescribing shortcuts"],
    status_code=200,
    response_model=s.UpdateTemplateResponse,
)
async def update_template(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    template_id: UUID,
    data: s.UpdateTemplateInput,
):
    result = await invoke(
        ctx,
        "update_template",
        service.update_template,
        data.model_dump(exclude_unset=True),
        params={"template_id": template_id},
        response_model=s.UpdateTemplateResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/prescription-templates/{template_id}/archive",
    tags=["Prescribing shortcuts"],
    status_code=201,
    response_model=s.ArchiveTemplateResponse,
)
async def archive_template(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    template_id: UUID,
    data: s.ArchiveTemplateInput,
):
    result = await invoke(
        ctx,
        "archive_template",
        service.archive_template,
        data.model_dump(exclude_unset=True),
        params={"template_id": template_id},
        response_model=s.ArchiveTemplateResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.post(
    "/patients/{patient_id}/prescription-ocr-jobs",
    tags=["Prescription OCR"],
    status_code=202,
    response_model=s.CreateOcrJobResponse,
)
async def create_ocr_job(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    patient_id: UUID,
    data: s.CreateOcrJobInput,
):
    result = await invoke(
        ctx,
        "create_ocr_job",
        service.create_ocr_job,
        data.model_dump(exclude_unset=True),
        params={"patient_id": patient_id},
        response_model=s.CreateOcrJobResponse,
        status=202,
        idempotent=True,
    )
    return result


@router.get(
    "/patients/{patient_id}/prescription-ocr-jobs",
    tags=["Prescription OCR"],
    status_code=200,
    response_model=s.ListOcrJobsResponse,
)
async def list_ocr_jobs(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    patient_id: UUID,
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
    status: Annotated[str | None, Query(alias="status", max_length=200)] = None,
):
    result = await invoke(
        ctx,
        "list_ocr_jobs",
        service.list_ocr_jobs,
        None,
        params={"patient_id": patient_id, "page": page, "page_size": page_size, "status": status},
        response_model=s.ListOcrJobsResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.get(
    "/prescription-ocr-jobs/{job_id}",
    tags=["Prescription OCR"],
    status_code=200,
    response_model=s.OcrJobDetailResponse,
)
async def ocr_job_detail(request: Request, ctx: Annotated[Context, Depends(context)], job_id: UUID):
    result = await invoke(
        ctx,
        "ocr_job_detail",
        service.ocr_job_detail,
        None,
        params={"job_id": job_id},
        response_model=s.OcrJobDetailResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/prescription-ocr-jobs/{job_id}/retry",
    tags=["Prescription OCR"],
    status_code=202,
    response_model=s.RetryOcrJobResponse,
)
async def retry_ocr_job(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    job_id: UUID,
    data: s.RetryOcrJobInput,
):
    result = await invoke(
        ctx,
        "retry_ocr_job",
        service.retry_ocr_job,
        data.model_dump(exclude_unset=True),
        params={"job_id": job_id},
        response_model=s.RetryOcrJobResponse,
        status=202,
        idempotent=False,
    )
    return result


@router.post(
    "/patients/{patient_id}/prescription-ocr-jobs/{job_id}/draft",
    tags=["Prescription OCR"],
    status_code=201,
    response_model=s.ConfirmOcrDraftResponse,
)
async def confirm_ocr_draft(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    patient_id: UUID,
    job_id: UUID,
    data: s.ConfirmOcrDraftInput,
):
    result = await invoke(
        ctx,
        "confirm_ocr_draft",
        service.confirm_ocr_draft,
        data.model_dump(exclude_unset=True),
        params={"patient_id": patient_id, "job_id": job_id},
        response_model=s.ConfirmOcrDraftResponse,
        status=201,
        idempotent=True,
    )
    return result
