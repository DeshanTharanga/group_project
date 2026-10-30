"""Thin async HTTP routes. Domain services own permissions and state transitions."""

from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile

from app.core.security import Context, context, integration_context
from app.modules.integrations import schemas as s
from app.modules.integrations import service
from app.services.common import invoke

router = APIRouter()


@router.post(
    "/admin/integration-clients",
    tags=["Integration management"],
    status_code=201,
    response_model=s.CreateClientResponse,
)
async def create_client(
    request: Request, ctx: Annotated[Context, Depends(context)], data: s.CreateClientInput
):
    result = await invoke(
        ctx,
        "create_client",
        service.create_client,
        data.model_dump(exclude_unset=True),
        params={},
        response_model=s.CreateClientResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.get(
    "/admin/integration-clients",
    tags=["Integration management"],
    status_code=200,
    response_model=s.ListClientsResponse,
)
async def list_clients(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
):
    result = await invoke(
        ctx,
        "list_clients",
        service.list_clients,
        None,
        params={"page": page, "page_size": page_size},
        response_model=s.ListClientsResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/admin/integration-clients/{client_id}/rotate",
    tags=["Integration management"],
    status_code=201,
    response_model=s.RotateClientResponse,
)
async def rotate_client(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    client_id: UUID,
    data: s.RotateClientInput,
):
    result = await invoke(
        ctx,
        "rotate_client",
        service.rotate_client,
        data.model_dump(exclude_unset=True),
        params={"client_id": client_id},
        response_model=s.RotateClientResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.post(
    "/admin/integration-clients/{client_id}/revoke",
    tags=["Integration management"],
    status_code=201,
    response_model=s.RevokeClientResponse,
)
async def revoke_client(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    client_id: UUID,
    data: s.RevokeClientInput,
):
    result = await invoke(
        ctx,
        "revoke_client",
        service.revoke_client,
        data.model_dump(exclude_unset=True),
        params={"client_id": client_id},
        response_model=s.RevokeClientResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.post(
    "/admin/integration-clients/{client_id}/suspend",
    tags=["Integration management"],
    status_code=201,
    response_model=s.SuspendClientResponse,
)
async def suspend_client(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    client_id: UUID,
    data: s.SuspendClientInput,
):
    result = await invoke(
        ctx,
        "suspend_client",
        service.suspend_client,
        data.model_dump(exclude_unset=True),
        params={"client_id": client_id},
        response_model=s.SuspendClientResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.get(
    "/admin/integration-submissions",
    tags=["Integration management"],
    status_code=200,
    response_model=s.ListSubmissionsResponse,
)
async def list_submissions(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
    status: Annotated[str | None, Query(alias="status", max_length=200)] = None,
):
    result = await invoke(
        ctx,
        "list_submissions",
        service.list_submissions,
        None,
        params={"page": page, "page_size": page_size, "status": status},
        response_model=s.ListSubmissionsResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/integrations/reports",
    tags=["Mock integration"],
    status_code=201,
    response_model=s.IntegrationReportResponse,
)
async def integration_report(
    request: Request,
    ctx: Annotated[Context, Depends(integration_context)],
    file: Annotated[UploadFile, File()],
    request_token: Annotated[str, Form()],
    external_report_id: Annotated[str, Form()],
    report_type: Annotated[str, Form()],
    lab_reference: Annotated[str, Form()],
    report_date: Annotated[date | None, Form()] = None,
    notes: Annotated[str | None, Form()] = None,
):
    from app.modules.documents.storage import read_upload

    content = await read_upload(file)
    data = s.IntegrationReportInput(
        request_token=request_token,
        external_report_id=external_report_id,
        report_type=report_type,
        report_date=report_date,
        lab_reference=lab_reference,
        notes=notes,
    ).model_dump(exclude_unset=True)
    data.update(file=content, filename=file.filename or "upload")
    result = await invoke(
        ctx,
        "integration_report",
        service.integration_report,
        data,
        params={},
        response_model=s.IntegrationReportResponse,
        status=201,
        idempotent=True,
    )
    return result


@router.post(
    "/integrations/reports/{report_id}/versions",
    tags=["Mock integration"],
    status_code=201,
    response_model=s.IntegrationReportVersionResponse,
)
async def integration_report_version(
    request: Request,
    ctx: Annotated[Context, Depends(integration_context)],
    report_id: UUID,
    file: Annotated[UploadFile, File()],
    request_token: Annotated[str, Form()],
    external_report_id: Annotated[str, Form()],
    report_type: Annotated[str, Form()],
    lab_reference: Annotated[str, Form()],
    reason: Annotated[str, Form()],
    report_date: Annotated[date | None, Form()] = None,
    notes: Annotated[str | None, Form()] = None,
):
    from app.modules.documents.storage import read_upload

    content = await read_upload(file)
    data = s.IntegrationReportVersionInput(
        request_token=request_token,
        external_report_id=external_report_id,
        report_type=report_type,
        report_date=report_date,
        lab_reference=lab_reference,
        notes=notes,
        reason=reason,
    ).model_dump(exclude_unset=True)
    data.update(file=content, filename=file.filename or "upload")
    result = await invoke(
        ctx,
        "integration_report_version",
        service.integration_report_version,
        data,
        params={"report_id": report_id},
        response_model=s.IntegrationReportVersionResponse,
        status=201,
        idempotent=True,
    )
    return result
