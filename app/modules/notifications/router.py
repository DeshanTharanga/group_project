"""Thin async HTTP routes. Domain services own permissions and state transitions."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from app.core.security import Context, context
from app.modules.notifications import schemas as s
from app.modules.notifications import service
from app.services.common import invoke

router = APIRouter()


@router.get(
    "/me/notifications",
    tags=["Notifications"],
    status_code=200,
    response_model=s.ListNotificationsResponse,
)
async def list_notifications(
    request: Request,
    ctx: Annotated[Context, Depends(context)],
    page: Annotated[int, Query(alias="page", ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
    unread: Annotated[bool | None, Query(alias="unread")] = None,
):
    result = await invoke(
        ctx,
        "list_notifications",
        service.list_notifications,
        None,
        params={"page": page, "page_size": page_size, "unread": unread},
        response_model=s.ListNotificationsResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.post(
    "/notifications/{notification_id}/read",
    tags=["Notifications"],
    status_code=200,
    response_model=s.ReadNotificationResponse,
)
async def read_notification(
    request: Request, ctx: Annotated[Context, Depends(context)], notification_id: UUID
):
    result = await invoke(
        ctx,
        "read_notification",
        service.read_notification,
        None,
        params={"notification_id": notification_id},
        response_model=s.ReadNotificationResponse,
        status=200,
        idempotent=False,
    )
    return result
