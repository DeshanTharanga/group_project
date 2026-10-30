"""Typed interface transcribed from the supplied Developer Guide. Extra inputs are rejected."""

from datetime import date, datetime
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from app.core.schemas import InputModel


class CreateClientInput(InputModel):
    organization_id: UUID = Field(...)
    name: str = Field(..., min_length=1, max_length=200)
    scopes: list[str] = Field(..., min_length=1, max_length=1)
    expires_at: AwareDatetime = Field(...)


class CreateClientResponseClient(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    organization_id: UUID = Field(...)
    name: str = Field(...)
    scopes: list[str] = Field(...)
    status: str = Field(...)
    expires_at: datetime = Field(...)
    created_by: UUID = Field(...)
    created_at: datetime = Field(...)
    revoked_at: datetime | None = Field(None)


class CreateClientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    client: CreateClientResponseClient = Field(...)
    credential: str = Field(...)


class ListClientsResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    organization_id: UUID = Field(...)
    name: str = Field(...)
    scopes: list[str] = Field(...)
    status: str = Field(...)
    expires_at: datetime = Field(...)
    created_by: UUID = Field(...)
    created_at: datetime = Field(...)
    revoked_at: datetime | None = Field(None)


class ListClientsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[ListClientsResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)


class RotateClientInput(InputModel):
    expires_at: AwareDatetime = Field(...)
    reason: str = Field(..., min_length=1, max_length=1000)


class RotateClientResponseClient(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    organization_id: UUID = Field(...)
    name: str = Field(...)
    scopes: list[str] = Field(...)
    status: str = Field(...)
    expires_at: datetime = Field(...)
    created_by: UUID = Field(...)
    created_at: datetime = Field(...)
    revoked_at: datetime | None = Field(None)


class RotateClientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    client: RotateClientResponseClient = Field(...)
    credential: str = Field(...)


class RevokeClientInput(InputModel):
    reason: str = Field(..., min_length=1, max_length=1000)


class RevokeClientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    organization_id: UUID = Field(...)
    name: str = Field(...)
    scopes: list[str] = Field(...)
    status: str = Field(...)
    expires_at: datetime = Field(...)
    created_by: UUID = Field(...)
    created_at: datetime = Field(...)
    revoked_at: datetime | None = Field(None)


class SuspendClientInput(InputModel):
    reason: str = Field(..., min_length=1, max_length=1000)


class SuspendClientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    organization_id: UUID = Field(...)
    name: str = Field(...)
    scopes: list[str] = Field(...)
    status: str = Field(...)
    expires_at: datetime = Field(...)
    created_by: UUID = Field(...)
    created_at: datetime = Field(...)
    revoked_at: datetime | None = Field(None)


class ListSubmissionsResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    client_id: UUID = Field(...)
    upload_request_id: UUID = Field(...)
    external_report_id: str = Field(...)
    idempotency_key: str = Field(...)
    status: str = Field(...)
    report_id: UUID | None = Field(None)
    received_at: datetime = Field(...)
    error_code: str | None = Field(None)


class ListSubmissionsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[ListSubmissionsResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)


class IntegrationReportInput(InputModel):
    request_token: str = Field(..., min_length=1, max_length=256)
    external_report_id: str = Field(..., min_length=1, max_length=150)
    report_type: str = Field(..., min_length=1, max_length=200)
    report_date: date | None = Field(None)
    lab_reference: str = Field(..., min_length=1, max_length=150)
    notes: str | None = Field(None, max_length=2000)


class IntegrationReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    client_id: UUID = Field(...)
    upload_request_id: UUID = Field(...)
    external_report_id: str = Field(...)
    idempotency_key: str = Field(...)
    status: str = Field(...)
    report_id: UUID | None = Field(None)
    received_at: datetime = Field(...)
    error_code: str | None = Field(None)


class IntegrationReportVersionInput(InputModel):
    request_token: str = Field(..., min_length=1, max_length=256)
    external_report_id: str = Field(..., min_length=1, max_length=150)
    report_type: str = Field(..., min_length=1, max_length=200)
    report_date: date | None = Field(None)
    lab_reference: str = Field(..., min_length=1, max_length=150)
    notes: str | None = Field(None, max_length=2000)
    reason: str = Field(..., min_length=1, max_length=1000)


class IntegrationReportVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    client_id: UUID = Field(...)
    upload_request_id: UUID = Field(...)
    external_report_id: str = Field(...)
    idempotency_key: str = Field(...)
    status: str = Field(...)
    report_id: UUID | None = Field(None)
    received_at: datetime = Field(...)
    error_code: str | None = Field(None)
