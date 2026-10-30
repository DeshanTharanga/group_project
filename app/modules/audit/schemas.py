"""Typed interface transcribed from the supplied Developer Guide. Extra inputs are rejected."""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.schemas import InputModel


class AdminUsersResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    email: str | None = Field(None)
    display_name: str = Field(...)
    phone: str | None = Field(None)
    status: str = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)


class AdminUsersResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[AdminUsersResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)


class SetUserStatusInput(InputModel):
    status: Literal["active", "suspended", "disabled"] = Field(...)
    reason: str = Field(..., min_length=1, max_length=1000)


class SetUserStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    email: str | None = Field(None)
    display_name: str = Field(...)
    phone: str | None = Field(None)
    status: str = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)


class AssignAdminInput(InputModel):
    user_id: UUID = Field(...)
    role: Literal["admin"] = Field(...)
    reason: str = Field(..., min_length=1, max_length=1000)


class AssignAdminResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    status: str = Field(...)
    updated_at: datetime | None = Field(None)


class RevokeAdminInput(InputModel):
    reason: str = Field(..., min_length=1, max_length=1000)


class RevokeAdminResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    status: str = Field(...)
    updated_at: datetime | None = Field(None)


class OperationsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    pending_verifications: int = Field(...)
    active_organizations: int = Field(...)
    failed_jobs: int = Field(...)
    last_backup_at: datetime | None = Field(...)


class ListJobsResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    job_type: str = Field(...)
    status: str = Field(...)
    attempt_count: int = Field(...)
    error_code: str | None = Field(None)
    updated_at: datetime = Field(...)


class ListJobsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[ListJobsResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)


class RetryJobInput(InputModel):
    reason: str = Field(..., min_length=1, max_length=1000)


class RetryJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    job_type: str = Field(...)
    status: str = Field(...)
    attempt_count: int = Field(...)
    error_code: str | None = Field(None)
    updated_at: datetime = Field(...)


class ListAuditResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    actor_user_id: UUID | None = Field(None)
    actor_client_id: UUID | None = Field(None)
    action: str = Field(...)
    target_type: str = Field(...)
    target_id: UUID | None = Field(None)
    outcome: str = Field(...)
    request_id: str = Field(...)
    metadata: dict[str, Any] = Field(...)
    created_at: datetime = Field(...)


class ListAuditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[ListAuditResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)


class PatientActivityResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    action: str = Field(...)
    target_type: str = Field(...)
    target_id: UUID | None = Field(None)
    outcome: str = Field(...)
    created_at: datetime = Field(...)


class PatientActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[PatientActivityResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)
