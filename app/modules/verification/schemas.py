"""Typed interface transcribed from the supplied Developer Guide. Extra inputs are rejected."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.schemas import InputModel


class SubmitVerificationInput(InputModel):
    organization_id: UUID | None = Field(None)
    role: Literal["doctor", "pharmacist", "lab_staff"] = Field(...)
    registration_number: str = Field(..., min_length=1, max_length=100)
    evidence_document_ids: list[UUID] = Field(...)


class SubmitVerificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    user_id: UUID = Field(...)
    organization_id: UUID | None = Field(None)
    role: str = Field(...)
    registration_number: str | None = Field(None)
    status: str = Field(...)
    submitted_at: datetime = Field(...)
    reviewed_by: UUID | None = Field(None)
    reviewed_at: datetime | None = Field(None)
    review_reason: str | None = Field(None)
    evidence_document_ids: list[UUID] | None = Field(None)


class OwnVerificationsResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    user_id: UUID = Field(...)
    organization_id: UUID | None = Field(None)
    role: str = Field(...)
    registration_number: str | None = Field(None)
    status: str = Field(...)
    submitted_at: datetime = Field(...)
    reviewed_by: UUID | None = Field(None)
    reviewed_at: datetime | None = Field(None)
    review_reason: str | None = Field(None)
    evidence_document_ids: list[UUID] | None = Field(None)


class OwnVerificationsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[OwnVerificationsResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)


class AdminVerificationsResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    user_id: UUID = Field(...)
    organization_id: UUID | None = Field(None)
    role: str = Field(...)
    registration_number: str | None = Field(None)
    status: str = Field(...)
    submitted_at: datetime = Field(...)
    reviewed_by: UUID | None = Field(None)
    reviewed_at: datetime | None = Field(None)
    review_reason: str | None = Field(None)
    evidence_document_ids: list[UUID] | None = Field(None)


class AdminVerificationsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[AdminVerificationsResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)


class VerificationDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    user_id: UUID = Field(...)
    organization_id: UUID | None = Field(None)
    role: str = Field(...)
    registration_number: str | None = Field(None)
    status: str = Field(...)
    submitted_at: datetime = Field(...)
    reviewed_by: UUID | None = Field(None)
    reviewed_at: datetime | None = Field(None)
    review_reason: str | None = Field(None)
    evidence_document_ids: list[UUID] | None = Field(None)


class DecideVerificationInput(InputModel):
    status: Literal["approved", "rejected", "more_info_requested"] = Field(...)
    reason: str = Field(..., min_length=1, max_length=1000)


class DecideVerificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    user_id: UUID = Field(...)
    organization_id: UUID | None = Field(None)
    role: str = Field(...)
    registration_number: str | None = Field(None)
    status: str = Field(...)
    submitted_at: datetime = Field(...)
    reviewed_by: UUID | None = Field(None)
    reviewed_at: datetime | None = Field(None)
    review_reason: str | None = Field(None)
    evidence_document_ids: list[UUID] | None = Field(None)
