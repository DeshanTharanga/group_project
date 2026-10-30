"""Typed interface transcribed from the supplied Developer Guide. Extra inputs are rejected."""

from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.schemas import InputModel


class CreateLabRequestInput(InputModel):
    laboratory_id: UUID = Field(...)


class CreateLabRequestResponseRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    laboratory_id: UUID = Field(...)
    expires_at: datetime = Field(...)
    status: str = Field(...)
    created_at: datetime = Field(...)
    used_at: datetime | None = Field(None)


class CreateLabRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    request: CreateLabRequestResponseRequest = Field(...)
    request_token: str = Field(...)


class OwnLabRequestsResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    laboratory_id: UUID = Field(...)
    expires_at: datetime = Field(...)
    status: str = Field(...)
    created_at: datetime = Field(...)
    used_at: datetime | None = Field(None)


class OwnLabRequestsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[OwnLabRequestsResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)


class RevokeLabRequestInput(InputModel):
    reason: str = Field(..., min_length=1, max_length=1000)


class RevokeLabRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    laboratory_id: UUID = Field(...)
    expires_at: datetime = Field(...)
    status: str = Field(...)
    created_at: datetime = Field(...)
    used_at: datetime | None = Field(None)


class ResolveLabRequestInput(InputModel):
    request_token: str = Field(..., min_length=1, max_length=256)
    laboratory_id: UUID = Field(...)


class ResolveLabRequestResponsePatient(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    patient_user_id: UUID = Field(...)
    display_name: str = Field(...)
    date_of_birth: date | None = Field(None)


class ResolveLabRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    request_id: UUID = Field(...)
    patient: ResolveLabRequestResponsePatient = Field(...)
    laboratory_id: UUID = Field(...)
    expires_at: datetime = Field(...)


class PublishReportInput(InputModel):
    upload_request_id: UUID | None = Field(None)
    document_id: UUID = Field(...)
    report_type: str = Field(..., min_length=1, max_length=200)
    report_date: date | None = Field(None)
    lab_reference: str | None = Field(None, max_length=150)
    notes: str | None = Field(None, max_length=2000)


class PublishReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    laboratory_id: UUID | None = Field(None)
    report_identity_id: UUID | None = Field(None)
    upload_request_id: UUID | None = Field(None)
    document_id: UUID = Field(...)
    report_type: str = Field(...)
    report_date: date | None = Field(None)
    notes: str | None = Field(None)
    source: str = Field(...)
    uploaded_by: UUID | None = Field(None)
    status: str = Field(...)
    created_at: datetime = Field(...)
    supersedes_id: UUID | None = Field(None)
    correction_reason: str | None = Field(None)


class ListReportsResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    laboratory_id: UUID | None = Field(None)
    report_identity_id: UUID | None = Field(None)
    upload_request_id: UUID | None = Field(None)
    document_id: UUID = Field(...)
    report_type: str = Field(...)
    report_date: date | None = Field(None)
    notes: str | None = Field(None)
    source: str = Field(...)
    uploaded_by: UUID | None = Field(None)
    status: str = Field(...)
    created_at: datetime = Field(...)
    supersedes_id: UUID | None = Field(None)
    correction_reason: str | None = Field(None)


class ListReportsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[ListReportsResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)


class ReportDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    laboratory_id: UUID | None = Field(None)
    report_identity_id: UUID | None = Field(None)
    upload_request_id: UUID | None = Field(None)
    document_id: UUID = Field(...)
    report_type: str = Field(...)
    report_date: date | None = Field(None)
    notes: str | None = Field(None)
    source: str = Field(...)
    uploaded_by: UUID | None = Field(None)
    status: str = Field(...)
    created_at: datetime = Field(...)
    supersedes_id: UUID | None = Field(None)
    correction_reason: str | None = Field(None)


class LaboratoryReportsResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    laboratory_id: UUID | None = Field(None)
    report_identity_id: UUID | None = Field(None)
    upload_request_id: UUID | None = Field(None)
    document_id: UUID = Field(...)
    report_type: str = Field(...)
    report_date: date | None = Field(None)
    notes: str | None = Field(None)
    source: str = Field(...)
    uploaded_by: UUID | None = Field(None)
    status: str = Field(...)
    created_at: datetime = Field(...)
    supersedes_id: UUID | None = Field(None)
    correction_reason: str | None = Field(None)


class LaboratoryReportsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[LaboratoryReportsResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)


class ReplaceReportInput(InputModel):
    upload_request_id: UUID | None = Field(None)
    document_id: UUID = Field(...)
    report_type: str = Field(..., min_length=1, max_length=200)
    report_date: date | None = Field(None)
    lab_reference: str | None = Field(None, max_length=150)
    notes: str | None = Field(None, max_length=2000)
    reason: str = Field(..., min_length=1, max_length=1000)


class ReplaceReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    laboratory_id: UUID | None = Field(None)
    report_identity_id: UUID | None = Field(None)
    upload_request_id: UUID | None = Field(None)
    document_id: UUID = Field(...)
    report_type: str = Field(...)
    report_date: date | None = Field(None)
    notes: str | None = Field(None)
    source: str = Field(...)
    uploaded_by: UUID | None = Field(None)
    status: str = Field(...)
    created_at: datetime = Field(...)
    supersedes_id: UUID | None = Field(None)
    correction_reason: str | None = Field(None)


class WithdrawReportInput(InputModel):
    reason: str = Field(..., min_length=1, max_length=1000)


class WithdrawReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    laboratory_id: UUID | None = Field(None)
    report_identity_id: UUID | None = Field(None)
    upload_request_id: UUID | None = Field(None)
    document_id: UUID = Field(...)
    report_type: str = Field(...)
    report_date: date | None = Field(None)
    notes: str | None = Field(None)
    source: str = Field(...)
    uploaded_by: UUID | None = Field(None)
    status: str = Field(...)
    created_at: datetime = Field(...)
    supersedes_id: UUID | None = Field(None)
    correction_reason: str | None = Field(None)


class ReportHistoryResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    laboratory_id: UUID | None = Field(None)
    report_identity_id: UUID | None = Field(None)
    upload_request_id: UUID | None = Field(None)
    document_id: UUID = Field(...)
    report_type: str = Field(...)
    report_date: date | None = Field(None)
    notes: str | None = Field(None)
    source: str = Field(...)
    uploaded_by: UUID | None = Field(None)
    status: str = Field(...)
    created_at: datetime = Field(...)
    supersedes_id: UUID | None = Field(None)
    correction_reason: str | None = Field(None)


class ReportHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[ReportHistoryResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)


class UploadDocumentInput(InputModel):
    document_type: Literal["prescription", "report", "verification_evidence"] = Field(...)
    upload_request_id: UUID | None = Field(None)
    verification_application_id: UUID | None = Field(None)
    supersedes_id: UUID | None = Field(None)


class UploadDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    owner_user_id: UUID = Field(...)
    patient_user_id: UUID | None = Field(None)
    uploaded_by: UUID | None = Field(None)
    source: str = Field(...)
    document_type: str = Field(...)
    original_filename: str = Field(...)
    media_type: str = Field(...)
    byte_size: int = Field(...)
    sha256: str | None = Field(None)
    status: str = Field(...)
    created_at: datetime = Field(...)
    supersedes_id: UUID | None = Field(None)


class UploadVerificationDocumentInput(InputModel):
    document_type: Literal["prescription", "report", "verification_evidence"] = Field(...)
    upload_request_id: UUID | None = Field(None)
    verification_application_id: UUID | None = Field(None)
    supersedes_id: UUID | None = Field(None)


class UploadVerificationDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    owner_user_id: UUID = Field(...)
    patient_user_id: UUID | None = Field(None)
    uploaded_by: UUID | None = Field(None)
    source: str = Field(...)
    document_type: str = Field(...)
    original_filename: str = Field(...)
    media_type: str = Field(...)
    byte_size: int = Field(...)
    sha256: str | None = Field(None)
    status: str = Field(...)
    created_at: datetime = Field(...)
    supersedes_id: UUID | None = Field(None)


class DocumentDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    owner_user_id: UUID = Field(...)
    patient_user_id: UUID | None = Field(None)
    uploaded_by: UUID | None = Field(None)
    source: str = Field(...)
    document_type: str = Field(...)
    original_filename: str = Field(...)
    media_type: str = Field(...)
    byte_size: int = Field(...)
    sha256: str | None = Field(None)
    status: str = Field(...)
    created_at: datetime = Field(...)
    supersedes_id: UUID | None = Field(None)
