"""Thin async HTTP routes. Domain services own permissions and state transitions."""

from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile
from pydantic import AwareDatetime

from app.core.security import Context, context
from app.modules.documents import schemas as s
from app.modules.documents import service
from app.services.common import invoke

router = APIRouter()


@router.post(
    "/lab-upload-requests",
    tags=["Laboratory"],
    status_code=201,
    response_model=s.CreateLabRequestResponse,
)
async def create_lab_request(
    request: Request, ctx: Annotated[Context, Depends(context)], data: s.CreateLabRequestInput
):
    result = await invoke(
        ctx,
        "create_lab_request",
        service.create_lab_request,
        data.model_dump(exclude_unset=True),
        params={},
        response_model=s.CreateLabRequestResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.get(
    "/me/lab-upload-requests",
    tags=["Laboratory"],
    status_code=200,
    response_model=s.OwnLabRequestsResponse,
)
async def own_lab_requests(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
):
    result = await invoke(
        ctx,
        "own_lab_requests",
        service.own_lab_requests,
        None,
        params={"page": page, "page_size": page_size},
        response_model=s.OwnLabRequestsResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/lab-upload-requests/{request_id}/revoke",
    tags=["Laboratory"],
    status_code=201,
    response_model=s.RevokeLabRequestResponse,
)
async def revoke_lab_request(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    request_id: UUID,
    data: s.RevokeLabRequestInput,
):
    result = await invoke(
        ctx,
        "revoke_lab_request",
        service.revoke_lab_request,
        data.model_dump(exclude_unset=True),
        params={"request_id": request_id},
        response_model=s.RevokeLabRequestResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.post(
    "/lab-upload-requests/resolve",
    tags=["Laboratory"],
    status_code=200,
    response_model=s.ResolveLabRequestResponse,
)
async def resolve_lab_request(
    request: Request, ctx: Annotated[Context, Depends(context)], data: s.ResolveLabRequestInput
):
    result = await invoke(
        ctx,
        "resolve_lab_request",
        service.resolve_lab_request,
        data.model_dump(exclude_unset=True),
        params={},
        response_model=s.ResolveLabRequestResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/patients/{patient_id}/reports",
    tags=["Laboratory"],
    status_code=201,
    response_model=s.PublishReportResponse,
)
async def publish_report(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    patient_id: UUID,
    data: s.PublishReportInput,
):
    result = await invoke(
        ctx,
        "publish_report",
        service.publish_report,
        data.model_dump(exclude_unset=True),
        params={"patient_id": patient_id},
        response_model=s.PublishReportResponse,
        status=201,
        idempotent=True,
    )
    return result


@router.get(
    "/patients/{patient_id}/reports",
    tags=["Laboratory"],
    status_code=200,
    response_model=s.ListReportsResponse,
)
async def list_reports(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    patient_id: UUID,
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
    from_: Annotated[AwareDatetime | None, Query(alias="from")] = None,
    to: Annotated[AwareDatetime | None, Query(alias="to")] = None,
    status: Annotated[str | None, Query(alias="status", max_length=200)] = None,
):
    result = await invoke(
        ctx,
        "list_reports",
        service.list_reports,
        None,
        params={
            "patient_id": patient_id,
            "page": page,
            "page_size": page_size,
            "from": from_,
            "to": to,
            "status": status,
        },
        response_model=s.ListReportsResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.get(
    "/reports/{report_id}",
    tags=["Laboratory"],
    status_code=200,
    response_model=s.ReportDetailResponse,
)
async def report_detail(
    request: Request, ctx: Annotated[Context, Depends(context)], report_id: UUID
):
    result = await invoke(
        ctx,
        "report_detail",
        service.report_detail,
        None,
        params={"report_id": report_id},
        response_model=s.ReportDetailResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.get(
    "/me/laboratory-reports",
    tags=["Laboratory"],
    status_code=200,
    response_model=s.LaboratoryReportsResponse,
)
async def laboratory_reports(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
    from_: Annotated[AwareDatetime | None, Query(alias="from")] = None,
    to: Annotated[AwareDatetime | None, Query(alias="to")] = None,
):
    result = await invoke(
        ctx,
        "laboratory_reports",
        service.laboratory_reports,
        None,
        params={"page": page, "page_size": page_size, "from": from_, "to": to},
        response_model=s.LaboratoryReportsResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/reports/{report_id}/versions",
    tags=["Laboratory"],
    status_code=201,
    response_model=s.ReplaceReportResponse,
)
async def replace_report(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    report_id: UUID,
    data: s.ReplaceReportInput,
):
    result = await invoke(
        ctx,
        "replace_report",
        service.replace_report,
        data.model_dump(exclude_unset=True),
        params={"report_id": report_id},
        response_model=s.ReplaceReportResponse,
        status=201,
        idempotent=True,
    )
    return result


@router.post(
    "/reports/{report_id}/withdraw",
    tags=["Laboratory"],
    status_code=201,
    response_model=s.WithdrawReportResponse,
)
async def withdraw_report(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    report_id: UUID,
    data: s.WithdrawReportInput,
):
    result = await invoke(
        ctx,
        "withdraw_report",
        service.withdraw_report,
        data.model_dump(exclude_unset=True),
        params={"report_id": report_id},
        response_model=s.WithdrawReportResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.get(
    "/reports/{report_id}/history",
    tags=["Laboratory"],
    status_code=200,
    response_model=s.ReportHistoryResponse,
)
async def report_history(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    report_id: UUID,
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
):
    result = await invoke(
        ctx,
        "report_history",
        service.report_history,
        None,
        params={"report_id": report_id, "page": page, "page_size": page_size},
        response_model=s.ReportHistoryResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/patients/{patient_id}/documents",
    tags=["Documents"],
    status_code=201,
    response_model=s.UploadDocumentResponse,
)
async def upload_document(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    patient_id: UUID,
    file: Annotated[UploadFile, File()],
    document_type: Annotated[Literal["prescription", "report", "verification_evidence"], Form()],
    upload_request_id: Annotated[UUID | None, Form()] = None,
    verification_application_id: Annotated[UUID | None, Form()] = None,
    supersedes_id: Annotated[UUID | None, Form()] = None,
):
    from app.modules.documents.storage import read_upload

    content = await read_upload(file)
    data = s.UploadDocumentInput(
        document_type=document_type,
        upload_request_id=upload_request_id,
        verification_application_id=verification_application_id,
        supersedes_id=supersedes_id,
    ).model_dump(exclude_unset=True)
    data.update(file=content, filename=file.filename or "upload")
    result = await invoke(
        ctx,
        "upload_document",
        service.upload_document,
        data,
        params={"patient_id": patient_id},
        response_model=s.UploadDocumentResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.post(
    "/me/verification-documents",
    tags=["Documents"],
    status_code=201,
    response_model=s.UploadVerificationDocumentResponse,
)
async def upload_verification_document(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    file: Annotated[UploadFile, File()],
    document_type: Annotated[Literal["prescription", "report", "verification_evidence"], Form()],
    upload_request_id: Annotated[UUID | None, Form()] = None,
    verification_application_id: Annotated[UUID | None, Form()] = None,
    supersedes_id: Annotated[UUID | None, Form()] = None,
):
    from app.modules.documents.storage import read_upload

    content = await read_upload(file)
    data = s.UploadVerificationDocumentInput(
        document_type=document_type,
        upload_request_id=upload_request_id,
        verification_application_id=verification_application_id,
        supersedes_id=supersedes_id,
    ).model_dump(exclude_unset=True)
    data.update(file=content, filename=file.filename or "upload")
    result = await invoke(
        ctx,
        "upload_verification_document",
        service.upload_verification_document,
        data,
        params={},
        response_model=s.UploadVerificationDocumentResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.get(
    "/documents/{document_id}",
    tags=["Documents"],
    status_code=200,
    response_model=s.DocumentDetailResponse,
)
async def document_detail(
    request: Request, ctx: Annotated[Context, Depends(context)], document_id: UUID
):
    result = await invoke(
        ctx,
        "document_detail",
        service.document_detail,
        None,
        params={"document_id": document_id},
        response_model=s.DocumentDetailResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.get("/documents/{document_id}/content", tags=["Documents"], status_code=200)
async def document_content(
    request: Request, ctx: Annotated[Context, Depends(context)], document_id: UUID
):
    result = await invoke(
        ctx,
        "document_content",
        service.document_content,
        None,
        params={"document_id": document_id},
        response_model=None,
        status=200,
        idempotent=False,
    )
    return result
