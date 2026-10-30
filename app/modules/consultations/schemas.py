"""Typed interface transcribed from the supplied Developer Guide. Extra inputs are rejected."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.schemas import InputModel


class StartConsultationInput(InputModel):
    grant_id: UUID = Field(...)


class StartConsultationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    doctor_user_id: UUID = Field(...)
    organization_id: UUID | None = Field(None)
    grant_id: UUID = Field(...)
    started_at: datetime = Field(...)
    ended_at: datetime | None = Field(None)
    summary: str | None = Field(None)


class ListConsultationsResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    doctor_user_id: UUID = Field(...)
    organization_id: UUID | None = Field(None)
    grant_id: UUID = Field(...)
    started_at: datetime = Field(...)
    ended_at: datetime | None = Field(None)
    summary: str | None = Field(None)


class ListConsultationsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[ListConsultationsResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)


class EndConsultationInput(InputModel):
    summary: str | None = Field(None, max_length=4000)


class EndConsultationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    doctor_user_id: UUID = Field(...)
    organization_id: UUID | None = Field(None)
    grant_id: UUID = Field(...)
    started_at: datetime = Field(...)
    ended_at: datetime | None = Field(None)
    summary: str | None = Field(None)
