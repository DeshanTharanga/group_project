"""Thin async HTTP routes. Domain services own permissions and state transitions."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from pydantic import AwareDatetime

from app.core.security import Context, context
from app.modules.audit import schemas as s
from app.modules.audit import service
from app.services.common import invoke

router = APIRouter()


@router.get(
    "/admin/users", tags=["Administration"], status_code=200, response_model=s.AdminUsersResponse
)
async def admin_users(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
    q: Annotated[str | None, Query(alias="q", max_length=200)] = None,
    status: Annotated[str | None, Query(alias="status", max_length=200)] = None,
):
    result = await invoke(
        ctx,
        "admin_users",
        service.admin_users,
        None,
        params={"page": page, "page_size": page_size, "q": q, "status": status},
        response_model=s.AdminUsersResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/admin/users/{user_id}/status",
    tags=["Administration"],
    status_code=201,
    response_model=s.SetUserStatusResponse,
)
async def set_user_status(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    user_id: UUID,
    data: s.SetUserStatusInput,
):
    result = await invoke(
        ctx,
        "set_user_status",
        service.set_user_status,
        data.model_dump(exclude_unset=True),
        params={"user_id": user_id},
        response_model=s.SetUserStatusResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.post(
    "/admin/role-assignments",
    tags=["Administration"],
    status_code=201,
    response_model=s.AssignAdminResponse,
)
async def assign_admin(
    request: Request, ctx: Annotated[Context, Depends(context)], data: s.AssignAdminInput
):
    result = await invoke(
        ctx,
        "assign_admin",
        service.assign_admin,
        data.model_dump(exclude_unset=True),
        params={},
        response_model=s.AssignAdminResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.post(
    "/admin/users/{user_id}/admin-role/revoke",
    tags=["Administration"],
    status_code=201,
    response_model=s.RevokeAdminResponse,
)
async def revoke_admin(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    user_id: UUID,
    data: s.RevokeAdminInput,
):
    result = await invoke(
        ctx,
        "revoke_admin",
        service.revoke_admin,
        data.model_dump(exclude_unset=True),
        params={"user_id": user_id},
        response_model=s.RevokeAdminResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.get(
    "/admin/operations",
    tags=["Administration"],
    status_code=200,
    response_model=s.OperationsResponse,
)
async def operations(request: Request, ctx: Annotated[Context, Depends(context)]):
    result = await invoke(
        ctx,
        "operations",
        service.operations,
        None,
        params={},
        response_model=s.OperationsResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.get(
    "/admin/jobs", tags=["Administration"], status_code=200, response_model=s.ListJobsResponse
)
async def list_jobs(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
    status: Annotated[str | None, Query(alias="status", max_length=200)] = None,
):
    result = await invoke(
        ctx,
        "list_jobs",
        service.list_jobs,
        None,
        params={"page": page, "page_size": page_size, "status": status},
        response_model=s.ListJobsResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/admin/jobs/{job_id}/retry",
    tags=["Administration"],
    status_code=202,
    response_model=s.RetryJobResponse,
)
async def retry_job(
    request: Request, ctx: Annotated[Context, Depends(context)], job_id: UUID, data: s.RetryJobInput
):
    result = await invoke(
        ctx,
        "retry_job",
        service.retry_job,
        data.model_dump(exclude_unset=True),
        params={"job_id": job_id},
        response_model=s.RetryJobResponse,
        status=202,
        idempotent=False,
    )
    return result


@router.get(
    "/admin/audit-events",
    tags=["Administration"],
    status_code=200,
    response_model=s.ListAuditResponse,
)
async def list_audit(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
    action: Annotated[str | None, Query(alias="action", max_length=200)] = None,
    from_: Annotated[AwareDatetime | None, Query(alias="from")] = None,
    to: Annotated[AwareDatetime | None, Query(alias="to")] = None,
    request_id: Annotated[UUID | None, Query(alias="request_id")] = None,
):
    result = await invoke(
        ctx,
        "list_audit",
        service.list_audit,
        None,
        params={
            "page": page,
            "page_size": page_size,
            "action": action,
            "from": from_,
            "to": to,
            "request_id": request_id,
        },
        response_model=s.ListAuditResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.get(
    "/patients/{patient_id}/activity",
    tags=["Administration"],
    status_code=200,
    response_model=s.PatientActivityResponse,
)
async def patient_activity(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    patient_id: UUID,
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
):
    result = await invoke(
        ctx,
        "patient_activity",
        service.patient_activity,
        None,
        params={"patient_id": patient_id, "page": page, "page_size": page_size},
        response_model=s.PatientActivityResponse,
        status=200,
        idempotent=False,
    )
    return result
