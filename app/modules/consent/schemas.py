"""Typed interface transcribed from the supplied Developer Guide. Extra inputs are rejected."""

from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.schemas import InputModel


class DoctorQrResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    doctor_reference: str = Field(...)
    qr_payload: str = Field(...)


class ResolveDoctorInput(InputModel):
    doctor_reference: str = Field(..., min_length=1, max_length=256)


class ResolveDoctorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: UUID = Field(...)
    display_name: str = Field(...)
    role: str = Field(...)
    verification_status: str = Field(...)
    organization_id: UUID | None = Field(None)
    organization_name: str | None = Field(None)


class CreateGrantInput(InputModel):
    doctor_reference: str = Field(...)
    organization_id: UUID | None = Field(None)
    categories: list[str] = Field(..., min_length=1)
    duration_hours: Literal[24, 168, 720] = Field(...)
    allow_consultation: bool = Field(...)


class CreateGrantResponseGrant(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    professional_user_id: UUID = Field(...)
    organization_id: UUID | None = Field(None)
    allow_consultation: bool = Field(...)
    status: str = Field(...)
    starts_at: datetime = Field(...)
    expires_at: datetime = Field(...)
    revoked_at: datetime | None = Field(None)
    created_at: datetime = Field(...)


class CreateGrantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    grant: CreateGrantResponseGrant = Field(...)
    categories: list[str] = Field(...)


class OwnGrantsResponseItemsGrant(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    professional_user_id: UUID = Field(...)
    organization_id: UUID | None = Field(None)
    allow_consultation: bool = Field(...)
    status: str = Field(...)
    starts_at: datetime = Field(...)
    expires_at: datetime = Field(...)
    revoked_at: datetime | None = Field(None)
    created_at: datetime = Field(...)


class OwnGrantsResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    grant: OwnGrantsResponseItemsGrant = Field(...)
    categories: list[str] = Field(...)


class OwnGrantsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[OwnGrantsResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)


class RevokeGrantInput(InputModel):
    reason: str = Field(..., min_length=1, max_length=1000)


class RevokeGrantResponseGrant(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    professional_user_id: UUID = Field(...)
    organization_id: UUID | None = Field(None)
    allow_consultation: bool = Field(...)
    status: str = Field(...)
    starts_at: datetime = Field(...)
    expires_at: datetime = Field(...)
    revoked_at: datetime | None = Field(None)
    created_at: datetime = Field(...)


class RevokeGrantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    grant: RevokeGrantResponseGrant = Field(...)
    categories: list[str] = Field(...)


class PatientQueueResponseItemsPatient(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    patient_user_id: UUID = Field(...)
    display_name: str = Field(...)
    date_of_birth: date | None = Field(None)


class PatientQueueResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    patient: PatientQueueResponseItemsPatient = Field(...)
    grant_id: UUID = Field(...)
    categories: list[str] = Field(...)
    expires_at: datetime = Field(...)
    allow_consultation: bool = Field(...)


class PatientQueueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[PatientQueueResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)
