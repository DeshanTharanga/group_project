"""Thin async HTTP routes. Domain services own permissions and state transitions."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from pydantic import AwareDatetime

from app.core.security import Context, context
from app.modules.medication import schemas as s
from app.modules.medication import service
from app.services.common import invoke

router = APIRouter()


@router.post(
    "/patients/{patient_id}/medication-schedules",
    tags=["Medication"],
    status_code=201,
    response_model=s.CreateScheduleResponse,
)
async def create_schedule(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    patient_id: UUID,
    data: s.CreateScheduleInput,
):
    result = await invoke(
        ctx,
        "create_schedule",
        service.create_schedule,
        data.model_dump(exclude_unset=True),
        params={"patient_id": patient_id},
        response_model=s.CreateScheduleResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.get(
    "/patients/{patient_id}/medication-schedules",
    tags=["Medication"],
    status_code=200,
    response_model=s.ListSchedulesResponse,
)
async def list_schedules(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    patient_id: UUID,
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
    status: Annotated[str | None, Query(alias="status", max_length=200)] = None,
):
    result = await invoke(
        ctx,
        "list_schedules",
        service.list_schedules,
        None,
        params={"patient_id": patient_id, "page": page, "page_size": page_size, "status": status},
        response_model=s.ListSchedulesResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/medication-schedules/{schedule_id}/status",
    tags=["Medication"],
    status_code=201,
    response_model=s.ScheduleStatusResponse,
)
async def schedule_status(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    schedule_id: UUID,
    data: s.ScheduleStatusInput,
):
    result = await invoke(
        ctx,
        "schedule_status",
        service.schedule_status,
        data.model_dump(exclude_unset=True),
        params={"schedule_id": schedule_id},
        response_model=s.ScheduleStatusResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.post(
    "/medication-schedules/{schedule_id}/replacement",
    tags=["Medication"],
    status_code=201,
    response_model=s.ReplaceScheduleResponse,
)
async def replace_schedule(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    schedule_id: UUID,
    data: s.ReplaceScheduleInput,
):
    result = await invoke(
        ctx,
        "replace_schedule",
        service.replace_schedule,
        data.model_dump(exclude_unset=True),
        params={"schedule_id": schedule_id},
        response_model=s.ReplaceScheduleResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.get(
    "/patients/{patient_id}/dose-occurrences",
    tags=["Medication"],
    status_code=200,
    response_model=s.ListOccurrencesResponse,
)
async def list_occurrences(
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
        "list_occurrences",
        service.list_occurrences,
        None,
        params={
            "patient_id": patient_id,
            "page": page,
            "page_size": page_size,
            "from": from_,
            "to": to,
            "status": status,
        },
        response_model=s.ListOccurrencesResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/dose-occurrences/{occurrence_id}/snooze",
    tags=["Medication"],
    status_code=201,
    response_model=s.SnoozeOccurrenceResponse,
)
async def snooze_occurrence(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    occurrence_id: UUID,
    data: s.SnoozeOccurrenceInput,
):
    result = await invoke(
        ctx,
        "snooze_occurrence",
        service.snooze_occurrence,
        data.model_dump(exclude_unset=True),
        params={"occurrence_id": occurrence_id},
        response_model=s.SnoozeOccurrenceResponse,
        status=201,
        idempotent=False,
    )
    return result


@router.post(
    "/dose-occurrences/{occurrence_id}/responses",
    tags=["Medication"],
    status_code=201,
    response_model=s.RespondOccurrenceResponse,
)
async def respond_occurrence(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    occurrence_id: UUID,
    data: s.RespondOccurrenceInput,
):
    result = await invoke(
        ctx,
        "respond_occurrence",
        service.respond_occurrence,
        data.model_dump(exclude_unset=True),
        params={"occurrence_id": occurrence_id},
        response_model=s.RespondOccurrenceResponse,
        status=201,
        idempotent=True,
    )
    return result


@router.get(
    "/dose-occurrences/{occurrence_id}/responses",
    tags=["Medication"],
    status_code=200,
    response_model=s.ListResponsesResponse,
)
async def list_responses(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    occurrence_id: UUID,
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
):
    result = await invoke(
        ctx,
        "list_responses",
        service.list_responses,
        None,
        params={"occurrence_id": occurrence_id, "page": page, "page_size": page_size},
        response_model=s.ListResponsesResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/medication-logs/{log_id}/corrections",
    tags=["Medication"],
    status_code=201,
    response_model=s.CorrectLogResponse,
)
async def correct_log(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    log_id: UUID,
    data: s.CorrectLogInput,
):
    result = await invoke(
        ctx,
        "correct_log",
        service.correct_log,
        data.model_dump(exclude_unset=True),
        params={"log_id": log_id},
        response_model=s.CorrectLogResponse,
        status=201,
        idempotent=True,
    )
    return result


@router.get(
    "/patients/{patient_id}/adherence",
    tags=["Medication"],
    status_code=200,
    response_model=s.AdherenceResponse,
)
async def adherence(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    patient_id: UUID,
    from_: Annotated[AwareDatetime, Query(alias="from")],
    to: Annotated[AwareDatetime, Query(alias="to")],
):
    result = await invoke(
        ctx,
        "adherence",
        service.adherence,
        None,
        params={"patient_id": patient_id, "from": from_, "to": to},
        response_model=s.AdherenceResponse,
        status=200,
        idempotent=False,
    )
    return result
