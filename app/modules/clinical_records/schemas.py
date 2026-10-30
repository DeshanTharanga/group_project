"""Typed interface transcribed from the supplied Developer Guide. Extra inputs are rejected."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from app.core.schemas import InputModel


class ListClinicalRecordsResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    consultation_id: UUID | None = Field(None)
    type: str = Field(...)
    title: str = Field(...)
    description: str | None = Field(None)
    clinical_code: str | None = Field(None)
    source: str = Field(...)
    recorded_by: UUID = Field(...)
    status: str = Field(...)
    recorded_at: datetime = Field(...)
    created_at: datetime = Field(...)
    supersedes_id: UUID | None = Field(None)
    correction_reason: str | None = Field(None)


class ListClinicalRecordsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[ListClinicalRecordsResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)


class CreateClinicalRecordInput(InputModel):
    consultation_id: UUID | None = Field(None)
    type: Literal["condition", "diagnosis", "allergy", "note"] = Field(...)
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=8000)
    clinical_code: str | None = Field(None, max_length=100)
    recorded_at: AwareDatetime = Field(...)


class CreateClinicalRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    consultation_id: UUID | None = Field(None)
    type: str = Field(...)
    title: str = Field(...)
    description: str | None = Field(None)
    clinical_code: str | None = Field(None)
    source: str = Field(...)
    recorded_by: UUID = Field(...)
    status: str = Field(...)
    recorded_at: datetime = Field(...)
    created_at: datetime = Field(...)
    supersedes_id: UUID | None = Field(None)
    correction_reason: str | None = Field(None)


class ReplaceClinicalRecordInput(InputModel):
    consultation_id: UUID | None = Field(None)
    type: Literal["condition", "diagnosis", "allergy", "note"] = Field(...)
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=8000)
    clinical_code: str | None = Field(None, max_length=100)
    recorded_at: AwareDatetime = Field(...)
    reason: str = Field(..., min_length=1, max_length=1000)


class ReplaceClinicalRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    consultation_id: UUID | None = Field(None)
    type: str = Field(...)
    title: str = Field(...)
    description: str | None = Field(None)
    clinical_code: str | None = Field(None)
    source: str = Field(...)
    recorded_by: UUID = Field(...)
    status: str = Field(...)
    recorded_at: datetime = Field(...)
    created_at: datetime = Field(...)
    supersedes_id: UUID | None = Field(None)
    correction_reason: str | None = Field(None)


class ClinicalHistoryResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    consultation_id: UUID | None = Field(None)
    type: str = Field(...)
    title: str = Field(...)
    description: str | None = Field(None)
    clinical_code: str | None = Field(None)
    source: str = Field(...)
    recorded_by: UUID = Field(...)
    status: str = Field(...)
    recorded_at: datetime = Field(...)
    created_at: datetime = Field(...)
    supersedes_id: UUID | None = Field(None)
    correction_reason: str | None = Field(None)


class ClinicalHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[ClinicalHistoryResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)


class ClinicalDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    consultation_id: UUID | None = Field(None)
    type: str = Field(...)
    title: str = Field(...)
    description: str | None = Field(None)
    clinical_code: str | None = Field(None)
    source: str = Field(...)
    recorded_by: UUID = Field(...)
    status: str = Field(...)
    recorded_at: datetime = Field(...)
    created_at: datetime = Field(...)
    supersedes_id: UUID | None = Field(None)
    correction_reason: str | None = Field(None)


class RequestCorrectionInput(InputModel):
    reason: str = Field(..., min_length=1, max_length=1000)


class RequestCorrectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    condition_id: UUID | None = Field(None)
    diagnosis_id: UUID | None = Field(None)
    allergy_id: UUID | None = Field(None)
    clinical_note_id: UUID | None = Field(None)
    requested_by: UUID = Field(...)
    reason: str = Field(...)
    request_status: str = Field(...)
    reviewed_by: UUID | None = Field(None)
    reviewed_at: datetime | None = Field(None)
    resolution_reason: str | None = Field(None)
    replacement_record_type: str | None = Field(None)
    replacement_record_id: UUID | None = Field(None)
    created_at: datetime = Field(...)


class ListCorrectionsResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    condition_id: UUID | None = Field(None)
    diagnosis_id: UUID | None = Field(None)
    allergy_id: UUID | None = Field(None)
    clinical_note_id: UUID | None = Field(None)
    requested_by: UUID = Field(...)
    reason: str = Field(...)
    request_status: str = Field(...)
    reviewed_by: UUID | None = Field(None)
    reviewed_at: datetime | None = Field(None)
    resolution_reason: str | None = Field(None)
    replacement_record_type: str | None = Field(None)
    replacement_record_id: UUID | None = Field(None)
    created_at: datetime = Field(...)


class ListCorrectionsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[ListCorrectionsResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)


class DecideCorrectionInput(InputModel):
    request_status: Literal["accepted", "rejected", "resolved"] = Field(...)
    reason: str = Field(..., min_length=1, max_length=1000)
    replacement_record_id: UUID | None = Field(None)


class DecideCorrectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    condition_id: UUID | None = Field(None)
    diagnosis_id: UUID | None = Field(None)
    allergy_id: UUID | None = Field(None)
    clinical_note_id: UUID | None = Field(None)
    requested_by: UUID = Field(...)
    reason: str = Field(...)
    request_status: str = Field(...)
    reviewed_by: UUID | None = Field(None)
    reviewed_at: datetime | None = Field(None)
    resolution_reason: str | None = Field(None)
    replacement_record_type: str | None = Field(None)
    replacement_record_id: UUID | None = Field(None)
    created_at: datetime = Field(...)
