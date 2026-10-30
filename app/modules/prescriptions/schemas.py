"""Typed interface transcribed from the supplied Developer Guide. Extra inputs are rejected."""

from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.schemas import InputModel


class ListMedicinesResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    generic_name: str = Field(...)
    brand_name: str | None = Field(None)
    strength: str | None = Field(None)
    form: str | None = Field(None)
    is_sample: bool = Field(...)
    created_at: datetime = Field(...)


class ListMedicinesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[ListMedicinesResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)


class CreateMedicineInput(InputModel):
    generic_name: str = Field(..., min_length=1, max_length=200)
    brand_name: str | None = Field(None, max_length=200)
    strength: str | None = Field(None, max_length=100)
    form: str | None = Field(None, max_length=100)


class CreateMedicineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    generic_name: str = Field(...)
    brand_name: str | None = Field(None)
    strength: str | None = Field(None)
    form: str | None = Field(None)
    is_sample: bool = Field(...)
    created_at: datetime = Field(...)


class ListPrescriptionsResponseItemsPrescription(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    consultation_id: UUID | None = Field(None)
    prescriber_user_id: UUID | None = Field(None)
    source: str = Field(...)
    claimed_prescriber: str | None = Field(None)
    review_status: str = Field(...)
    reviewed_by: UUID | None = Field(None)
    reviewed_at: datetime | None = Field(None)
    status: str = Field(...)
    issued_at: datetime | None = Field(None)
    starts_on: date | None = Field(None)
    ends_on: date | None = Field(None)
    previous_prescription_id: UUID | None = Field(None)
    original_document_id: UUID | None = Field(None)
    created_by: UUID = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
    version: int = Field(...)
    status_reason: str | None = Field(None)


class ListPrescriptionsResponseItemsItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    medicine_id: UUID | None = Field(None)
    medicine_name_snapshot: str = Field(...)
    dose_text: str = Field(...)
    route: str | None = Field(None)
    frequency: str = Field(...)
    duration_days: int | None = Field(None)
    instructions: str | None = Field(None)
    quantity: float | None = Field(None)
    quantity_unit: str | None = Field(None)
    is_prn: bool = Field(...)
    created_at: datetime = Field(...)


class ListPrescriptionsResponseItemsReviews(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    reviewer_user_id: UUID = Field(...)
    outcome: str = Field(...)
    notes: str | None = Field(None)
    reviewed_at: datetime = Field(...)


class ListPrescriptionsResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    prescription: ListPrescriptionsResponseItemsPrescription = Field(...)
    items: list[ListPrescriptionsResponseItemsItems] = Field(...)
    reviews: list[ListPrescriptionsResponseItemsReviews] = Field(...)


class ListPrescriptionsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[ListPrescriptionsResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)


class CreatePrescriptionInputItems(InputModel):
    medicine_id: UUID | None = Field(None)
    medicine_name_snapshot: str = Field(..., min_length=1, max_length=200)
    dose_text: str = Field(..., min_length=1, max_length=200)
    route: str | None = Field(None, max_length=100)
    frequency: str = Field(..., min_length=1, max_length=200)
    duration_days: int | None = Field(None, ge=1)
    instructions: str | None = Field(None, max_length=2000)
    quantity: Decimal | None = Field(
        None, gt=0, allow_inf_nan=False, max_digits=12, decimal_places=3
    )
    quantity_unit: Literal["tablet", "capsule", "mL"] | None = Field(None)
    is_prn: bool = Field(...)


class CreatePrescriptionInput(InputModel):
    consultation_id: UUID | None = Field(None)
    claimed_prescriber: str | None = Field(None, max_length=200)
    starts_on: date | None = Field(None)
    ends_on: date | None = Field(None)
    original_document_id: UUID | None = Field(None)
    items: list[CreatePrescriptionInputItems] = Field(..., min_length=1)


class CreatePrescriptionResponsePrescription(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    consultation_id: UUID | None = Field(None)
    prescriber_user_id: UUID | None = Field(None)
    source: str = Field(...)
    claimed_prescriber: str | None = Field(None)
    review_status: str = Field(...)
    reviewed_by: UUID | None = Field(None)
    reviewed_at: datetime | None = Field(None)
    status: str = Field(...)
    issued_at: datetime | None = Field(None)
    starts_on: date | None = Field(None)
    ends_on: date | None = Field(None)
    previous_prescription_id: UUID | None = Field(None)
    original_document_id: UUID | None = Field(None)
    created_by: UUID = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
    version: int = Field(...)
    status_reason: str | None = Field(None)


class CreatePrescriptionResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    medicine_id: UUID | None = Field(None)
    medicine_name_snapshot: str = Field(...)
    dose_text: str = Field(...)
    route: str | None = Field(None)
    frequency: str = Field(...)
    duration_days: int | None = Field(None)
    instructions: str | None = Field(None)
    quantity: float | None = Field(None)
    quantity_unit: str | None = Field(None)
    is_prn: bool = Field(...)
    created_at: datetime = Field(...)


class CreatePrescriptionResponseReviews(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    reviewer_user_id: UUID = Field(...)
    outcome: str = Field(...)
    notes: str | None = Field(None)
    reviewed_at: datetime = Field(...)


class CreatePrescriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    prescription: CreatePrescriptionResponsePrescription = Field(...)
    items: list[CreatePrescriptionResponseItems] = Field(...)
    reviews: list[CreatePrescriptionResponseReviews] = Field(...)


class PrescriptionDetailResponsePrescription(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    consultation_id: UUID | None = Field(None)
    prescriber_user_id: UUID | None = Field(None)
    source: str = Field(...)
    claimed_prescriber: str | None = Field(None)
    review_status: str = Field(...)
    reviewed_by: UUID | None = Field(None)
    reviewed_at: datetime | None = Field(None)
    status: str = Field(...)
    issued_at: datetime | None = Field(None)
    starts_on: date | None = Field(None)
    ends_on: date | None = Field(None)
    previous_prescription_id: UUID | None = Field(None)
    original_document_id: UUID | None = Field(None)
    created_by: UUID = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
    version: int = Field(...)
    status_reason: str | None = Field(None)


class PrescriptionDetailResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    medicine_id: UUID | None = Field(None)
    medicine_name_snapshot: str = Field(...)
    dose_text: str = Field(...)
    route: str | None = Field(None)
    frequency: str = Field(...)
    duration_days: int | None = Field(None)
    instructions: str | None = Field(None)
    quantity: float | None = Field(None)
    quantity_unit: str | None = Field(None)
    is_prn: bool = Field(...)
    created_at: datetime = Field(...)


class PrescriptionDetailResponseReviews(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    reviewer_user_id: UUID = Field(...)
    outcome: str = Field(...)
    notes: str | None = Field(None)
    reviewed_at: datetime = Field(...)


class PrescriptionDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    prescription: PrescriptionDetailResponsePrescription = Field(...)
    items: list[PrescriptionDetailResponseItems] = Field(...)
    reviews: list[PrescriptionDetailResponseReviews] = Field(...)


class UpdateDraftInputItems(InputModel):
    medicine_id: UUID | None = Field(None)
    medicine_name_snapshot: str = Field(..., min_length=1, max_length=200)
    dose_text: str = Field(..., min_length=1, max_length=200)
    route: str | None = Field(None, max_length=100)
    frequency: str = Field(..., min_length=1, max_length=200)
    duration_days: int | None = Field(None, ge=1)
    instructions: str | None = Field(None, max_length=2000)
    quantity: Decimal | None = Field(
        None, gt=0, allow_inf_nan=False, max_digits=12, decimal_places=3
    )
    quantity_unit: Literal["tablet", "capsule", "mL"] | None = Field(None)
    is_prn: bool = Field(...)


class UpdateDraftInput(InputModel):
    consultation_id: UUID | None = Field(None)
    claimed_prescriber: str | None = Field(None, max_length=200)
    starts_on: date | None = Field(None)
    ends_on: date | None = Field(None)
    original_document_id: UUID | None = Field(None)
    items: list[UpdateDraftInputItems] = Field(..., min_length=1)


class UpdateDraftResponsePrescription(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    consultation_id: UUID | None = Field(None)
    prescriber_user_id: UUID | None = Field(None)
    source: str = Field(...)
    claimed_prescriber: str | None = Field(None)
    review_status: str = Field(...)
    reviewed_by: UUID | None = Field(None)
    reviewed_at: datetime | None = Field(None)
    status: str = Field(...)
    issued_at: datetime | None = Field(None)
    starts_on: date | None = Field(None)
    ends_on: date | None = Field(None)
    previous_prescription_id: UUID | None = Field(None)
    original_document_id: UUID | None = Field(None)
    created_by: UUID = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
    version: int = Field(...)
    status_reason: str | None = Field(None)


class UpdateDraftResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    medicine_id: UUID | None = Field(None)
    medicine_name_snapshot: str = Field(...)
    dose_text: str = Field(...)
    route: str | None = Field(None)
    frequency: str = Field(...)
    duration_days: int | None = Field(None)
    instructions: str | None = Field(None)
    quantity: float | None = Field(None)
    quantity_unit: str | None = Field(None)
    is_prn: bool = Field(...)
    created_at: datetime = Field(...)


class UpdateDraftResponseReviews(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    reviewer_user_id: UUID = Field(...)
    outcome: str = Field(...)
    notes: str | None = Field(None)
    reviewed_at: datetime = Field(...)


class UpdateDraftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    prescription: UpdateDraftResponsePrescription = Field(...)
    items: list[UpdateDraftResponseItems] = Field(...)
    reviews: list[UpdateDraftResponseReviews] = Field(...)


class ConfirmPrescriptionResponsePrescription(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    consultation_id: UUID | None = Field(None)
    prescriber_user_id: UUID | None = Field(None)
    source: str = Field(...)
    claimed_prescriber: str | None = Field(None)
    review_status: str = Field(...)
    reviewed_by: UUID | None = Field(None)
    reviewed_at: datetime | None = Field(None)
    status: str = Field(...)
    issued_at: datetime | None = Field(None)
    starts_on: date | None = Field(None)
    ends_on: date | None = Field(None)
    previous_prescription_id: UUID | None = Field(None)
    original_document_id: UUID | None = Field(None)
    created_by: UUID = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
    version: int = Field(...)
    status_reason: str | None = Field(None)


class ConfirmPrescriptionResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    medicine_id: UUID | None = Field(None)
    medicine_name_snapshot: str = Field(...)
    dose_text: str = Field(...)
    route: str | None = Field(None)
    frequency: str = Field(...)
    duration_days: int | None = Field(None)
    instructions: str | None = Field(None)
    quantity: float | None = Field(None)
    quantity_unit: str | None = Field(None)
    is_prn: bool = Field(...)
    created_at: datetime = Field(...)


class ConfirmPrescriptionResponseReviews(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    reviewer_user_id: UUID = Field(...)
    outcome: str = Field(...)
    notes: str | None = Field(None)
    reviewed_at: datetime = Field(...)


class ConfirmPrescriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    prescription: ConfirmPrescriptionResponsePrescription = Field(...)
    items: list[ConfirmPrescriptionResponseItems] = Field(...)
    reviews: list[ConfirmPrescriptionResponseReviews] = Field(...)


class IssuePrescriptionResponsePrescription(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    consultation_id: UUID | None = Field(None)
    prescriber_user_id: UUID | None = Field(None)
    source: str = Field(...)
    claimed_prescriber: str | None = Field(None)
    review_status: str = Field(...)
    reviewed_by: UUID | None = Field(None)
    reviewed_at: datetime | None = Field(None)
    status: str = Field(...)
    issued_at: datetime | None = Field(None)
    starts_on: date | None = Field(None)
    ends_on: date | None = Field(None)
    previous_prescription_id: UUID | None = Field(None)
    original_document_id: UUID | None = Field(None)
    created_by: UUID = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
    version: int = Field(...)
    status_reason: str | None = Field(None)


class IssuePrescriptionResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    medicine_id: UUID | None = Field(None)
    medicine_name_snapshot: str = Field(...)
    dose_text: str = Field(...)
    route: str | None = Field(None)
    frequency: str = Field(...)
    duration_days: int | None = Field(None)
    instructions: str | None = Field(None)
    quantity: float | None = Field(None)
    quantity_unit: str | None = Field(None)
    is_prn: bool = Field(...)
    created_at: datetime = Field(...)


class IssuePrescriptionResponseReviews(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    reviewer_user_id: UUID = Field(...)
    outcome: str = Field(...)
    notes: str | None = Field(None)
    reviewed_at: datetime = Field(...)


class IssuePrescriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    prescription: IssuePrescriptionResponsePrescription = Field(...)
    items: list[IssuePrescriptionResponseItems] = Field(...)
    reviews: list[IssuePrescriptionResponseReviews] = Field(...)


class ReviewPrescriptionInput(InputModel):
    outcome: Literal["reviewed", "needs_clarification", "not_accepted"] = Field(...)
    notes: str | None = Field(None, max_length=2000)


class ReviewPrescriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    reviewer_user_id: UUID = Field(...)
    outcome: str = Field(...)
    notes: str | None = Field(None)
    reviewed_at: datetime = Field(...)


class VersionPrescriptionInputItems(InputModel):
    medicine_id: UUID | None = Field(None)
    medicine_name_snapshot: str = Field(..., min_length=1, max_length=200)
    dose_text: str = Field(..., min_length=1, max_length=200)
    route: str | None = Field(None, max_length=100)
    frequency: str = Field(..., min_length=1, max_length=200)
    duration_days: int | None = Field(None, ge=1)
    instructions: str | None = Field(None, max_length=2000)
    quantity: Decimal | None = Field(
        None, gt=0, allow_inf_nan=False, max_digits=12, decimal_places=3
    )
    quantity_unit: Literal["tablet", "capsule", "mL"] | None = Field(None)
    is_prn: bool = Field(...)


class VersionPrescriptionInput(InputModel):
    consultation_id: UUID | None = Field(None)
    claimed_prescriber: str | None = Field(None, max_length=200)
    starts_on: date | None = Field(None)
    ends_on: date | None = Field(None)
    original_document_id: UUID | None = Field(None)
    items: list[VersionPrescriptionInputItems] = Field(..., min_length=1)
    reason: str = Field(..., min_length=1, max_length=1000)


class VersionPrescriptionResponsePrescription(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    consultation_id: UUID | None = Field(None)
    prescriber_user_id: UUID | None = Field(None)
    source: str = Field(...)
    claimed_prescriber: str | None = Field(None)
    review_status: str = Field(...)
    reviewed_by: UUID | None = Field(None)
    reviewed_at: datetime | None = Field(None)
    status: str = Field(...)
    issued_at: datetime | None = Field(None)
    starts_on: date | None = Field(None)
    ends_on: date | None = Field(None)
    previous_prescription_id: UUID | None = Field(None)
    original_document_id: UUID | None = Field(None)
    created_by: UUID = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
    version: int = Field(...)
    status_reason: str | None = Field(None)


class VersionPrescriptionResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    medicine_id: UUID | None = Field(None)
    medicine_name_snapshot: str = Field(...)
    dose_text: str = Field(...)
    route: str | None = Field(None)
    frequency: str = Field(...)
    duration_days: int | None = Field(None)
    instructions: str | None = Field(None)
    quantity: float | None = Field(None)
    quantity_unit: str | None = Field(None)
    is_prn: bool = Field(...)
    created_at: datetime = Field(...)


class VersionPrescriptionResponseReviews(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    reviewer_user_id: UUID = Field(...)
    outcome: str = Field(...)
    notes: str | None = Field(None)
    reviewed_at: datetime = Field(...)


class VersionPrescriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    prescription: VersionPrescriptionResponsePrescription = Field(...)
    items: list[VersionPrescriptionResponseItems] = Field(...)
    reviews: list[VersionPrescriptionResponseReviews] = Field(...)


class RenewPrescriptionInputItems(InputModel):
    medicine_id: UUID | None = Field(None)
    medicine_name_snapshot: str = Field(..., min_length=1, max_length=200)
    dose_text: str = Field(..., min_length=1, max_length=200)
    route: str | None = Field(None, max_length=100)
    frequency: str = Field(..., min_length=1, max_length=200)
    duration_days: int | None = Field(None, ge=1)
    instructions: str | None = Field(None, max_length=2000)
    quantity: Decimal | None = Field(
        None, gt=0, allow_inf_nan=False, max_digits=12, decimal_places=3
    )
    quantity_unit: Literal["tablet", "capsule", "mL"] | None = Field(None)
    is_prn: bool = Field(...)


class RenewPrescriptionInput(InputModel):
    consultation_id: UUID | None = Field(None)
    claimed_prescriber: str | None = Field(None, max_length=200)
    starts_on: date | None = Field(None)
    ends_on: date | None = Field(None)
    original_document_id: UUID | None = Field(None)
    items: list[RenewPrescriptionInputItems] = Field(..., min_length=1)
    reason: str = Field(..., min_length=1, max_length=1000)


class RenewPrescriptionResponsePrescription(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    consultation_id: UUID | None = Field(None)
    prescriber_user_id: UUID | None = Field(None)
    source: str = Field(...)
    claimed_prescriber: str | None = Field(None)
    review_status: str = Field(...)
    reviewed_by: UUID | None = Field(None)
    reviewed_at: datetime | None = Field(None)
    status: str = Field(...)
    issued_at: datetime | None = Field(None)
    starts_on: date | None = Field(None)
    ends_on: date | None = Field(None)
    previous_prescription_id: UUID | None = Field(None)
    original_document_id: UUID | None = Field(None)
    created_by: UUID = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
    version: int = Field(...)
    status_reason: str | None = Field(None)


class RenewPrescriptionResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    medicine_id: UUID | None = Field(None)
    medicine_name_snapshot: str = Field(...)
    dose_text: str = Field(...)
    route: str | None = Field(None)
    frequency: str = Field(...)
    duration_days: int | None = Field(None)
    instructions: str | None = Field(None)
    quantity: float | None = Field(None)
    quantity_unit: str | None = Field(None)
    is_prn: bool = Field(...)
    created_at: datetime = Field(...)


class RenewPrescriptionResponseReviews(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    reviewer_user_id: UUID = Field(...)
    outcome: str = Field(...)
    notes: str | None = Field(None)
    reviewed_at: datetime = Field(...)


class RenewPrescriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    prescription: RenewPrescriptionResponsePrescription = Field(...)
    items: list[RenewPrescriptionResponseItems] = Field(...)
    reviews: list[RenewPrescriptionResponseReviews] = Field(...)


class ReissuePrescriptionInputItems(InputModel):
    medicine_id: UUID | None = Field(None)
    medicine_name_snapshot: str = Field(..., min_length=1, max_length=200)
    dose_text: str = Field(..., min_length=1, max_length=200)
    route: str | None = Field(None, max_length=100)
    frequency: str = Field(..., min_length=1, max_length=200)
    duration_days: int | None = Field(None, ge=1)
    instructions: str | None = Field(None, max_length=2000)
    quantity: Decimal | None = Field(
        None, gt=0, allow_inf_nan=False, max_digits=12, decimal_places=3
    )
    quantity_unit: Literal["tablet", "capsule", "mL"] | None = Field(None)
    is_prn: bool = Field(...)


class ReissuePrescriptionInput(InputModel):
    consultation_id: UUID | None = Field(None)
    claimed_prescriber: str | None = Field(None, max_length=200)
    starts_on: date | None = Field(None)
    ends_on: date | None = Field(None)
    original_document_id: UUID | None = Field(None)
    items: list[ReissuePrescriptionInputItems] = Field(..., min_length=1)
    reason: str = Field(..., min_length=1, max_length=1000)


class ReissuePrescriptionResponsePrescription(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    consultation_id: UUID | None = Field(None)
    prescriber_user_id: UUID | None = Field(None)
    source: str = Field(...)
    claimed_prescriber: str | None = Field(None)
    review_status: str = Field(...)
    reviewed_by: UUID | None = Field(None)
    reviewed_at: datetime | None = Field(None)
    status: str = Field(...)
    issued_at: datetime | None = Field(None)
    starts_on: date | None = Field(None)
    ends_on: date | None = Field(None)
    previous_prescription_id: UUID | None = Field(None)
    original_document_id: UUID | None = Field(None)
    created_by: UUID = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
    version: int = Field(...)
    status_reason: str | None = Field(None)


class ReissuePrescriptionResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    medicine_id: UUID | None = Field(None)
    medicine_name_snapshot: str = Field(...)
    dose_text: str = Field(...)
    route: str | None = Field(None)
    frequency: str = Field(...)
    duration_days: int | None = Field(None)
    instructions: str | None = Field(None)
    quantity: float | None = Field(None)
    quantity_unit: str | None = Field(None)
    is_prn: bool = Field(...)
    created_at: datetime = Field(...)


class ReissuePrescriptionResponseReviews(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    reviewer_user_id: UUID = Field(...)
    outcome: str = Field(...)
    notes: str | None = Field(None)
    reviewed_at: datetime = Field(...)


class ReissuePrescriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    prescription: ReissuePrescriptionResponsePrescription = Field(...)
    items: list[ReissuePrescriptionResponseItems] = Field(...)
    reviews: list[ReissuePrescriptionResponseReviews] = Field(...)


class CancelPrescriptionInput(InputModel):
    reason: str = Field(..., min_length=1, max_length=1000)


class CancelPrescriptionResponsePrescription(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    consultation_id: UUID | None = Field(None)
    prescriber_user_id: UUID | None = Field(None)
    source: str = Field(...)
    claimed_prescriber: str | None = Field(None)
    review_status: str = Field(...)
    reviewed_by: UUID | None = Field(None)
    reviewed_at: datetime | None = Field(None)
    status: str = Field(...)
    issued_at: datetime | None = Field(None)
    starts_on: date | None = Field(None)
    ends_on: date | None = Field(None)
    previous_prescription_id: UUID | None = Field(None)
    original_document_id: UUID | None = Field(None)
    created_by: UUID = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
    version: int = Field(...)
    status_reason: str | None = Field(None)


class CancelPrescriptionResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    medicine_id: UUID | None = Field(None)
    medicine_name_snapshot: str = Field(...)
    dose_text: str = Field(...)
    route: str | None = Field(None)
    frequency: str = Field(...)
    duration_days: int | None = Field(None)
    instructions: str | None = Field(None)
    quantity: float | None = Field(None)
    quantity_unit: str | None = Field(None)
    is_prn: bool = Field(...)
    created_at: datetime = Field(...)


class CancelPrescriptionResponseReviews(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    reviewer_user_id: UUID = Field(...)
    outcome: str = Field(...)
    notes: str | None = Field(None)
    reviewed_at: datetime = Field(...)


class CancelPrescriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    prescription: CancelPrescriptionResponsePrescription = Field(...)
    items: list[CancelPrescriptionResponseItems] = Field(...)
    reviews: list[CancelPrescriptionResponseReviews] = Field(...)


class DiscontinuePrescriptionInput(InputModel):
    reason: str = Field(..., min_length=1, max_length=1000)


class DiscontinuePrescriptionResponsePrescription(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    consultation_id: UUID | None = Field(None)
    prescriber_user_id: UUID | None = Field(None)
    source: str = Field(...)
    claimed_prescriber: str | None = Field(None)
    review_status: str = Field(...)
    reviewed_by: UUID | None = Field(None)
    reviewed_at: datetime | None = Field(None)
    status: str = Field(...)
    issued_at: datetime | None = Field(None)
    starts_on: date | None = Field(None)
    ends_on: date | None = Field(None)
    previous_prescription_id: UUID | None = Field(None)
    original_document_id: UUID | None = Field(None)
    created_by: UUID = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
    version: int = Field(...)
    status_reason: str | None = Field(None)


class DiscontinuePrescriptionResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    medicine_id: UUID | None = Field(None)
    medicine_name_snapshot: str = Field(...)
    dose_text: str = Field(...)
    route: str | None = Field(None)
    frequency: str = Field(...)
    duration_days: int | None = Field(None)
    instructions: str | None = Field(None)
    quantity: float | None = Field(None)
    quantity_unit: str | None = Field(None)
    is_prn: bool = Field(...)
    created_at: datetime = Field(...)


class DiscontinuePrescriptionResponseReviews(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    reviewer_user_id: UUID = Field(...)
    outcome: str = Field(...)
    notes: str | None = Field(None)
    reviewed_at: datetime = Field(...)


class DiscontinuePrescriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    prescription: DiscontinuePrescriptionResponsePrescription = Field(...)
    items: list[DiscontinuePrescriptionResponseItems] = Field(...)
    reviews: list[DiscontinuePrescriptionResponseReviews] = Field(...)


class CompletePrescriptionInput(InputModel):
    reason: str = Field(..., min_length=1, max_length=1000)


class CompletePrescriptionResponsePrescription(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    consultation_id: UUID | None = Field(None)
    prescriber_user_id: UUID | None = Field(None)
    source: str = Field(...)
    claimed_prescriber: str | None = Field(None)
    review_status: str = Field(...)
    reviewed_by: UUID | None = Field(None)
    reviewed_at: datetime | None = Field(None)
    status: str = Field(...)
    issued_at: datetime | None = Field(None)
    starts_on: date | None = Field(None)
    ends_on: date | None = Field(None)
    previous_prescription_id: UUID | None = Field(None)
    original_document_id: UUID | None = Field(None)
    created_by: UUID = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
    version: int = Field(...)
    status_reason: str | None = Field(None)


class CompletePrescriptionResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    medicine_id: UUID | None = Field(None)
    medicine_name_snapshot: str = Field(...)
    dose_text: str = Field(...)
    route: str | None = Field(None)
    frequency: str = Field(...)
    duration_days: int | None = Field(None)
    instructions: str | None = Field(None)
    quantity: float | None = Field(None)
    quantity_unit: str | None = Field(None)
    is_prn: bool = Field(...)
    created_at: datetime = Field(...)


class CompletePrescriptionResponseReviews(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    reviewer_user_id: UUID = Field(...)
    outcome: str = Field(...)
    notes: str | None = Field(None)
    reviewed_at: datetime = Field(...)


class CompletePrescriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    prescription: CompletePrescriptionResponsePrescription = Field(...)
    items: list[CompletePrescriptionResponseItems] = Field(...)
    reviews: list[CompletePrescriptionResponseReviews] = Field(...)


class PrescriptionHistoryResponseItemsPrescription(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    consultation_id: UUID | None = Field(None)
    prescriber_user_id: UUID | None = Field(None)
    source: str = Field(...)
    claimed_prescriber: str | None = Field(None)
    review_status: str = Field(...)
    reviewed_by: UUID | None = Field(None)
    reviewed_at: datetime | None = Field(None)
    status: str = Field(...)
    issued_at: datetime | None = Field(None)
    starts_on: date | None = Field(None)
    ends_on: date | None = Field(None)
    previous_prescription_id: UUID | None = Field(None)
    original_document_id: UUID | None = Field(None)
    created_by: UUID = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
    version: int = Field(...)
    status_reason: str | None = Field(None)


class PrescriptionHistoryResponseItemsItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    medicine_id: UUID | None = Field(None)
    medicine_name_snapshot: str = Field(...)
    dose_text: str = Field(...)
    route: str | None = Field(None)
    frequency: str = Field(...)
    duration_days: int | None = Field(None)
    instructions: str | None = Field(None)
    quantity: float | None = Field(None)
    quantity_unit: str | None = Field(None)
    is_prn: bool = Field(...)
    created_at: datetime = Field(...)


class PrescriptionHistoryResponseItemsReviews(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    reviewer_user_id: UUID = Field(...)
    outcome: str = Field(...)
    notes: str | None = Field(None)
    reviewed_at: datetime = Field(...)


class PrescriptionHistoryResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    prescription: PrescriptionHistoryResponseItemsPrescription = Field(...)
    items: list[PrescriptionHistoryResponseItemsItems] = Field(...)
    reviews: list[PrescriptionHistoryResponseItemsReviews] = Field(...)


class PrescriptionHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[PrescriptionHistoryResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)


class ListTemplatesResponseItemsItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    medicine_id: UUID | None = Field(None)
    medicine_name_snapshot: str = Field(...)
    dose_text: str = Field(...)
    route: str | None = Field(None)
    frequency: str = Field(...)
    duration_days: int | None = Field(None)
    instructions: str | None = Field(None)
    quantity: float | None = Field(None)
    quantity_unit: str | None = Field(None)
    is_prn: bool = Field(...)


class ListTemplatesResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    doctor_user_id: UUID = Field(...)
    name: str = Field(...)
    template_type: str = Field(...)
    status: str = Field(...)
    items: list[ListTemplatesResponseItemsItems] = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)


class ListTemplatesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[ListTemplatesResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)


class CreateTemplateInputItems(InputModel):
    medicine_id: UUID | None = Field(None)
    medicine_name_snapshot: str = Field(..., min_length=1, max_length=200)
    dose_text: str = Field(..., min_length=1, max_length=200)
    route: str | None = Field(None, max_length=100)
    frequency: str = Field(..., min_length=1, max_length=200)
    duration_days: int | None = Field(None, ge=1)
    instructions: str | None = Field(None, max_length=2000)
    quantity: Decimal | None = Field(
        None, gt=0, allow_inf_nan=False, max_digits=12, decimal_places=3
    )
    quantity_unit: Literal["tablet", "capsule", "mL"] | None = Field(None)
    is_prn: bool = Field(...)


class CreateTemplateInput(InputModel):
    name: str = Field(..., min_length=1, max_length=120)
    template_type: Literal["favourite", "template"] = Field(...)
    items: list[CreateTemplateInputItems] = Field(..., min_length=1)


class CreateTemplateResponseTemplateItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    medicine_id: UUID | None = Field(None)
    medicine_name_snapshot: str = Field(...)
    dose_text: str = Field(...)
    route: str | None = Field(None)
    frequency: str = Field(...)
    duration_days: int | None = Field(None)
    instructions: str | None = Field(None)
    quantity: float | None = Field(None)
    quantity_unit: str | None = Field(None)
    is_prn: bool = Field(...)


class CreateTemplateResponseTemplate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    doctor_user_id: UUID = Field(...)
    name: str = Field(...)
    template_type: str = Field(...)
    status: str = Field(...)
    items: list[CreateTemplateResponseTemplateItems] = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)


class CreateTemplateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    template: CreateTemplateResponseTemplate = Field(...)


class UpdateTemplateInputItems(InputModel):
    medicine_id: UUID | None = Field(None)
    medicine_name_snapshot: str = Field(..., min_length=1, max_length=200)
    dose_text: str = Field(..., min_length=1, max_length=200)
    route: str | None = Field(None, max_length=100)
    frequency: str = Field(..., min_length=1, max_length=200)
    duration_days: int | None = Field(None, ge=1)
    instructions: str | None = Field(None, max_length=2000)
    quantity: Decimal | None = Field(
        None, gt=0, allow_inf_nan=False, max_digits=12, decimal_places=3
    )
    quantity_unit: Literal["tablet", "capsule", "mL"] | None = Field(None)
    is_prn: bool = Field(...)


class UpdateTemplateInput(InputModel):
    name: str | None = Field(None, min_length=1, max_length=120)
    items: list[UpdateTemplateInputItems] | None = Field(None, min_length=1)


class UpdateTemplateResponseTemplateItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    medicine_id: UUID | None = Field(None)
    medicine_name_snapshot: str = Field(...)
    dose_text: str = Field(...)
    route: str | None = Field(None)
    frequency: str = Field(...)
    duration_days: int | None = Field(None)
    instructions: str | None = Field(None)
    quantity: float | None = Field(None)
    quantity_unit: str | None = Field(None)
    is_prn: bool = Field(...)


class UpdateTemplateResponseTemplate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    doctor_user_id: UUID = Field(...)
    name: str = Field(...)
    template_type: str = Field(...)
    status: str = Field(...)
    items: list[UpdateTemplateResponseTemplateItems] = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)


class UpdateTemplateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    template: UpdateTemplateResponseTemplate = Field(...)


class ArchiveTemplateInput(InputModel):
    reason: str = Field(..., min_length=1, max_length=1000)


class ArchiveTemplateResponseTemplateItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    medicine_id: UUID | None = Field(None)
    medicine_name_snapshot: str = Field(...)
    dose_text: str = Field(...)
    route: str | None = Field(None)
    frequency: str = Field(...)
    duration_days: int | None = Field(None)
    instructions: str | None = Field(None)
    quantity: float | None = Field(None)
    quantity_unit: str | None = Field(None)
    is_prn: bool = Field(...)


class ArchiveTemplateResponseTemplate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    doctor_user_id: UUID = Field(...)
    name: str = Field(...)
    template_type: str = Field(...)
    status: str = Field(...)
    items: list[ArchiveTemplateResponseTemplateItems] = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)


class ArchiveTemplateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    template: ArchiveTemplateResponseTemplate = Field(...)


class CreateOcrJobInput(InputModel):
    original_document_id: UUID = Field(...)


class CreateOcrJobResponseExtractedFieldsItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    medicine_id: UUID | None = Field(None)
    medicine_name_snapshot: str = Field(...)
    dose_text: str = Field(...)
    route: str | None = Field(None)
    frequency: str = Field(...)
    duration_days: int | None = Field(None)
    instructions: str | None = Field(None)
    quantity: float | None = Field(None)
    quantity_unit: str | None = Field(None)
    is_prn: bool = Field(...)


class CreateOcrJobResponseExtractedFields(BaseModel):
    raw_text: str | None = None
    model_config = ConfigDict(from_attributes=True)
    claimed_prescriber: str | None = Field(None)
    starts_on: date | None = Field(None)
    ends_on: date | None = Field(None)
    items: list[CreateOcrJobResponseExtractedFieldsItems] | None = Field(None)


class CreateOcrJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    original_document_id: UUID = Field(...)
    status: str = Field(...)
    extracted_fields: CreateOcrJobResponseExtractedFields | None = Field(None)
    attempt_count: int = Field(...)
    error_code: str | None = Field(None)
    resulting_prescription_id: UUID | None = Field(None)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)


class ListOcrJobsResponseItemsExtractedFieldsItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    medicine_id: UUID | None = Field(None)
    medicine_name_snapshot: str = Field(...)
    dose_text: str = Field(...)
    route: str | None = Field(None)
    frequency: str = Field(...)
    duration_days: int | None = Field(None)
    instructions: str | None = Field(None)
    quantity: float | None = Field(None)
    quantity_unit: str | None = Field(None)
    is_prn: bool = Field(...)


class ListOcrJobsResponseItemsExtractedFields(BaseModel):
    raw_text: str | None = None
    model_config = ConfigDict(from_attributes=True)
    claimed_prescriber: str | None = Field(None)
    starts_on: date | None = Field(None)
    ends_on: date | None = Field(None)
    items: list[ListOcrJobsResponseItemsExtractedFieldsItems] | None = Field(None)


class ListOcrJobsResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    original_document_id: UUID = Field(...)
    status: str = Field(...)
    extracted_fields: ListOcrJobsResponseItemsExtractedFields | None = Field(None)
    attempt_count: int = Field(...)
    error_code: str | None = Field(None)
    resulting_prescription_id: UUID | None = Field(None)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)


class ListOcrJobsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[ListOcrJobsResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)


class OcrJobDetailResponseExtractedFieldsItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    medicine_id: UUID | None = Field(None)
    medicine_name_snapshot: str = Field(...)
    dose_text: str = Field(...)
    route: str | None = Field(None)
    frequency: str = Field(...)
    duration_days: int | None = Field(None)
    instructions: str | None = Field(None)
    quantity: float | None = Field(None)
    quantity_unit: str | None = Field(None)
    is_prn: bool = Field(...)


class OcrJobDetailResponseExtractedFields(BaseModel):
    raw_text: str | None = None
    model_config = ConfigDict(from_attributes=True)
    claimed_prescriber: str | None = Field(None)
    starts_on: date | None = Field(None)
    ends_on: date | None = Field(None)
    items: list[OcrJobDetailResponseExtractedFieldsItems] | None = Field(None)


class OcrJobDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    original_document_id: UUID = Field(...)
    status: str = Field(...)
    extracted_fields: OcrJobDetailResponseExtractedFields | None = Field(None)
    attempt_count: int = Field(...)
    error_code: str | None = Field(None)
    resulting_prescription_id: UUID | None = Field(None)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)


class RetryOcrJobInput(InputModel):
    reason: str = Field(..., min_length=1, max_length=1000)


class RetryOcrJobResponseExtractedFieldsItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    medicine_id: UUID | None = Field(None)
    medicine_name_snapshot: str = Field(...)
    dose_text: str = Field(...)
    route: str | None = Field(None)
    frequency: str = Field(...)
    duration_days: int | None = Field(None)
    instructions: str | None = Field(None)
    quantity: float | None = Field(None)
    quantity_unit: str | None = Field(None)
    is_prn: bool = Field(...)


class RetryOcrJobResponseExtractedFields(BaseModel):
    raw_text: str | None = None
    model_config = ConfigDict(from_attributes=True)
    claimed_prescriber: str | None = Field(None)
    starts_on: date | None = Field(None)
    ends_on: date | None = Field(None)
    items: list[RetryOcrJobResponseExtractedFieldsItems] | None = Field(None)


class RetryOcrJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    original_document_id: UUID = Field(...)
    status: str = Field(...)
    extracted_fields: RetryOcrJobResponseExtractedFields | None = Field(None)
    attempt_count: int = Field(...)
    error_code: str | None = Field(None)
    resulting_prescription_id: UUID | None = Field(None)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)


class ConfirmOcrDraftInputItems(InputModel):
    medicine_id: UUID | None = Field(None)
    medicine_name_snapshot: str = Field(..., min_length=1, max_length=200)
    dose_text: str = Field(..., min_length=1, max_length=200)
    route: str | None = Field(None, max_length=100)
    frequency: str = Field(..., min_length=1, max_length=200)
    duration_days: int | None = Field(None, ge=1)
    instructions: str | None = Field(None, max_length=2000)
    quantity: Decimal | None = Field(
        None, gt=0, allow_inf_nan=False, max_digits=12, decimal_places=3
    )
    quantity_unit: Literal["tablet", "capsule", "mL"] | None = Field(None)
    is_prn: bool = Field(...)


class ConfirmOcrDraftInput(InputModel):
    claimed_prescriber: str | None = Field(None, max_length=200)
    starts_on: date | None = Field(None)
    ends_on: date | None = Field(None)
    items: list[ConfirmOcrDraftInputItems] = Field(..., min_length=1)


class ConfirmOcrDraftResponseJobExtractedFieldsItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    medicine_id: UUID | None = Field(None)
    medicine_name_snapshot: str = Field(...)
    dose_text: str = Field(...)
    route: str | None = Field(None)
    frequency: str = Field(...)
    duration_days: int | None = Field(None)
    instructions: str | None = Field(None)
    quantity: float | None = Field(None)
    quantity_unit: str | None = Field(None)
    is_prn: bool = Field(...)


class ConfirmOcrDraftResponseJobExtractedFields(BaseModel):
    raw_text: str | None = None
    model_config = ConfigDict(from_attributes=True)
    claimed_prescriber: str | None = Field(None)
    starts_on: date | None = Field(None)
    ends_on: date | None = Field(None)
    items: list[ConfirmOcrDraftResponseJobExtractedFieldsItems] | None = Field(None)


class ConfirmOcrDraftResponseJob(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    original_document_id: UUID = Field(...)
    status: str = Field(...)
    extracted_fields: ConfirmOcrDraftResponseJobExtractedFields | None = Field(None)
    attempt_count: int = Field(...)
    error_code: str | None = Field(None)
    resulting_prescription_id: UUID | None = Field(None)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)


class ConfirmOcrDraftResponsePrescriptionPrescription(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    consultation_id: UUID | None = Field(None)
    prescriber_user_id: UUID | None = Field(None)
    source: str = Field(...)
    claimed_prescriber: str | None = Field(None)
    review_status: str = Field(...)
    reviewed_by: UUID | None = Field(None)
    reviewed_at: datetime | None = Field(None)
    status: str = Field(...)
    issued_at: datetime | None = Field(None)
    starts_on: date | None = Field(None)
    ends_on: date | None = Field(None)
    previous_prescription_id: UUID | None = Field(None)
    original_document_id: UUID | None = Field(None)
    created_by: UUID = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
    version: int = Field(...)
    status_reason: str | None = Field(None)


class ConfirmOcrDraftResponsePrescriptionItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    medicine_id: UUID | None = Field(None)
    medicine_name_snapshot: str = Field(...)
    dose_text: str = Field(...)
    route: str | None = Field(None)
    frequency: str = Field(...)
    duration_days: int | None = Field(None)
    instructions: str | None = Field(None)
    quantity: float | None = Field(None)
    quantity_unit: str | None = Field(None)
    is_prn: bool = Field(...)
    created_at: datetime = Field(...)


class ConfirmOcrDraftResponsePrescriptionReviews(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    reviewer_user_id: UUID = Field(...)
    outcome: str = Field(...)
    notes: str | None = Field(None)
    reviewed_at: datetime = Field(...)


class ConfirmOcrDraftResponsePrescription(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    prescription: ConfirmOcrDraftResponsePrescriptionPrescription = Field(...)
    items: list[ConfirmOcrDraftResponsePrescriptionItems] = Field(...)
    reviews: list[ConfirmOcrDraftResponsePrescriptionReviews] = Field(...)


class ConfirmOcrDraftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    job: ConfirmOcrDraftResponseJob = Field(...)
    prescription: ConfirmOcrDraftResponsePrescription = Field(...)
