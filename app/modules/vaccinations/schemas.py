"""Typed interface transcribed from the supplied Developer Guide. Extra inputs are rejected."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.schemas import InputModel


class ListVaccinationsResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    vaccine_name: str = Field(...)
    administered_on: date = Field(...)
    dose_details: str | None = Field(None)
    next_dose_on: date | None = Field(None)
    recorded_by: UUID = Field(...)
    source: str = Field(...)
    organization_id: UUID | None = Field(None)
    notes: str | None = Field(None)
    created_at: datetime = Field(...)
    supersedes_id: UUID | None = Field(None)
    correction_reason: str | None = Field(None)


class ListVaccinationsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[ListVaccinationsResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)


class CreateVaccinationInput(InputModel):
    consultation_id: UUID = Field(...)
    vaccine_name: str = Field(..., min_length=1, max_length=200)
    administered_on: date = Field(...)
    dose_details: str | None = Field(None, max_length=200)
    next_dose_on: date | None = Field(None)
    notes: str | None = Field(None, max_length=2000)


class CreateVaccinationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    vaccine_name: str = Field(...)
    administered_on: date = Field(...)
    dose_details: str | None = Field(None)
    next_dose_on: date | None = Field(None)
    recorded_by: UUID = Field(...)
    source: str = Field(...)
    organization_id: UUID | None = Field(None)
    notes: str | None = Field(None)
    created_at: datetime = Field(...)
    supersedes_id: UUID | None = Field(None)
    correction_reason: str | None = Field(None)


class ReplaceVaccinationInput(InputModel):
    consultation_id: UUID = Field(...)
    vaccine_name: str = Field(..., min_length=1, max_length=200)
    administered_on: date = Field(...)
    dose_details: str | None = Field(None, max_length=200)
    next_dose_on: date | None = Field(None)
    notes: str | None = Field(None, max_length=2000)
    reason: str = Field(..., min_length=1, max_length=1000)


class ReplaceVaccinationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    vaccine_name: str = Field(...)
    administered_on: date = Field(...)
    dose_details: str | None = Field(None)
    next_dose_on: date | None = Field(None)
    recorded_by: UUID = Field(...)
    source: str = Field(...)
    organization_id: UUID | None = Field(None)
    notes: str | None = Field(None)
    created_at: datetime = Field(...)
    supersedes_id: UUID | None = Field(None)
    correction_reason: str | None = Field(None)


class VaccinationHistoryResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    vaccine_name: str = Field(...)
    administered_on: date = Field(...)
    dose_details: str | None = Field(None)
    next_dose_on: date | None = Field(None)
    recorded_by: UUID = Field(...)
    source: str = Field(...)
    organization_id: UUID | None = Field(None)
    notes: str | None = Field(None)
    created_at: datetime = Field(...)
    supersedes_id: UUID | None = Field(None)
    correction_reason: str | None = Field(None)


class VaccinationHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[VaccinationHistoryResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)
