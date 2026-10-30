"""Typed interface transcribed from the supplied Developer Guide. Extra inputs are rejected."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ListNotificationsResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    user_id: UUID = Field(...)
    notification_type: str = Field(...)
    title: str = Field(...)
    body: str = Field(...)
    related_type: str | None = Field(None)
    related_id: UUID | None = Field(None)
    created_at: datetime = Field(...)
    read_at: datetime | None = Field(None)


class ListNotificationsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[ListNotificationsResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)


class ReadNotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    user_id: UUID = Field(...)
    notification_type: str = Field(...)
    title: str = Field(...)
    body: str = Field(...)
    related_type: str | None = Field(None)
    related_id: UUID | None = Field(None)
    created_at: datetime = Field(...)
    read_at: datetime | None = Field(None)
