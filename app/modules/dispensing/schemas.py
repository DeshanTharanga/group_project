"""Typed interface transcribed from the supplied Developer Guide. Extra inputs are rejected."""

from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.schemas import InputModel


class CreateShareInput(InputModel):
    prescription_id: UUID = Field(...)


class CreateShareResponseShare(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    status: str = Field(...)
    claim_expires_at: datetime = Field(...)
    claimed_by: UUID | None = Field(None)
    claimed_organization_id: UUID | None = Field(None)
    claimed_at: datetime | None = Field(None)
    confirmed_at: datetime | None = Field(None)
    confirmed_access_expires_at: datetime | None = Field(None)
    revoked_at: datetime | None = Field(None)
    created_at: datetime = Field(...)


class CreateShareResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    share: CreateShareResponseShare = Field(...)
    claim_token: str = Field(...)
    claim_expires_at: datetime = Field(...)


class OwnSharesResponseItemsShare(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    status: str = Field(...)
    claim_expires_at: datetime = Field(...)
    claimed_by: UUID | None = Field(None)
    claimed_organization_id: UUID | None = Field(None)
    claimed_at: datetime | None = Field(None)
    confirmed_at: datetime | None = Field(None)
    confirmed_access_expires_at: datetime | None = Field(None)
    revoked_at: datetime | None = Field(None)
    created_at: datetime = Field(...)


class OwnSharesResponseItemsPharmacist(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: UUID = Field(...)
    display_name: str = Field(...)
    role: str = Field(...)
    verification_status: str = Field(...)
    organization_id: UUID | None = Field(None)
    organization_name: str | None = Field(None)


class OwnSharesResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    share: OwnSharesResponseItemsShare = Field(...)
    pharmacist: OwnSharesResponseItemsPharmacist | None = Field(None)
    access_expires_at: datetime | None = Field(...)


class OwnSharesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[OwnSharesResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)


class ClaimShareInput(InputModel):
    claim_token: str = Field(..., min_length=1, max_length=256)
    organization_id: UUID = Field(...)


class ClaimShareResponseShare(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    status: str = Field(...)
    claim_expires_at: datetime = Field(...)
    claimed_by: UUID | None = Field(None)
    claimed_organization_id: UUID | None = Field(None)
    claimed_at: datetime | None = Field(None)
    confirmed_at: datetime | None = Field(None)
    confirmed_access_expires_at: datetime | None = Field(None)
    revoked_at: datetime | None = Field(None)
    created_at: datetime = Field(...)


class ClaimShareResponsePharmacist(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: UUID = Field(...)
    display_name: str = Field(...)
    role: str = Field(...)
    verification_status: str = Field(...)
    organization_id: UUID | None = Field(None)
    organization_name: str | None = Field(None)


class ClaimShareResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    share: ClaimShareResponseShare = Field(...)
    pharmacist: ClaimShareResponsePharmacist | None = Field(None)
    access_expires_at: datetime | None = Field(...)


class ShareDetailResponseShare(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    status: str = Field(...)
    claim_expires_at: datetime = Field(...)
    claimed_by: UUID | None = Field(None)
    claimed_organization_id: UUID | None = Field(None)
    claimed_at: datetime | None = Field(None)
    confirmed_at: datetime | None = Field(None)
    confirmed_access_expires_at: datetime | None = Field(None)
    revoked_at: datetime | None = Field(None)
    created_at: datetime = Field(...)


class ShareDetailResponsePharmacist(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: UUID = Field(...)
    display_name: str = Field(...)
    role: str = Field(...)
    verification_status: str = Field(...)
    organization_id: UUID | None = Field(None)
    organization_name: str | None = Field(None)


class ShareDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    share: ShareDetailResponseShare = Field(...)
    pharmacist: ShareDetailResponsePharmacist | None = Field(None)
    access_expires_at: datetime | None = Field(...)


class ConfirmShareResponseShare(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    status: str = Field(...)
    claim_expires_at: datetime = Field(...)
    claimed_by: UUID | None = Field(None)
    claimed_organization_id: UUID | None = Field(None)
    claimed_at: datetime | None = Field(None)
    confirmed_at: datetime | None = Field(None)
    confirmed_access_expires_at: datetime | None = Field(None)
    revoked_at: datetime | None = Field(None)
    created_at: datetime = Field(...)


class ConfirmShareResponsePharmacist(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: UUID = Field(...)
    display_name: str = Field(...)
    role: str = Field(...)
    verification_status: str = Field(...)
    organization_id: UUID | None = Field(None)
    organization_name: str | None = Field(None)


class ConfirmShareResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    share: ConfirmShareResponseShare = Field(...)
    pharmacist: ConfirmShareResponsePharmacist | None = Field(None)
    access_expires_at: datetime | None = Field(...)


class RevokeShareInput(InputModel):
    reason: str = Field(..., min_length=1, max_length=1000)


class RevokeShareResponseShare(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    status: str = Field(...)
    claim_expires_at: datetime = Field(...)
    claimed_by: UUID | None = Field(None)
    claimed_organization_id: UUID | None = Field(None)
    claimed_at: datetime | None = Field(None)
    confirmed_at: datetime | None = Field(None)
    confirmed_access_expires_at: datetime | None = Field(None)
    revoked_at: datetime | None = Field(None)
    created_at: datetime = Field(...)


class RevokeShareResponsePharmacist(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: UUID = Field(...)
    display_name: str = Field(...)
    role: str = Field(...)
    verification_status: str = Field(...)
    organization_id: UUID | None = Field(None)
    organization_name: str | None = Field(None)


class RevokeShareResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    share: RevokeShareResponseShare = Field(...)
    pharmacist: RevokeShareResponsePharmacist | None = Field(None)
    access_expires_at: datetime | None = Field(...)


class SharedPrescriptionResponsePatient(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    patient_user_id: UUID = Field(...)
    display_name: str = Field(...)
    date_of_birth: date | None = Field(None)


class SharedPrescriptionResponseIssuer(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: UUID = Field(...)
    display_name: str = Field(...)
    role: str = Field(...)
    verification_status: str = Field(...)
    organization_id: UUID | None = Field(None)
    organization_name: str | None = Field(None)


class SharedPrescriptionResponseItemsItem(BaseModel):
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


class SharedPrescriptionResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    item: SharedPrescriptionResponseItemsItem = Field(...)
    dispensed_quantity: float = Field(...)
    remaining_quantity: float = Field(...)


class SharedPrescriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    prescription_id: UUID = Field(...)
    patient: SharedPrescriptionResponsePatient = Field(...)
    issuer: SharedPrescriptionResponseIssuer = Field(...)
    source: str = Field(...)
    status: str = Field(...)
    items: list[SharedPrescriptionResponseItems] = Field(...)


class DispenseInputItems(InputModel):
    prescription_item_id: UUID = Field(...)
    quantity: Decimal = Field(..., gt=0, allow_inf_nan=False, max_digits=12, decimal_places=3)
    quantity_unit: Literal["tablet", "capsule", "mL"] = Field(...)


class DispenseInput(InputModel):
    share_id: UUID = Field(...)
    organization_id: UUID = Field(...)
    items: list[DispenseInputItems] = Field(..., min_length=1)
    notes: str | None = Field(None, max_length=1000)


class DispenseResponseEvent(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    pharmacist_user_id: UUID = Field(...)
    organization_id: UUID = Field(...)
    share_id: UUID | None = Field(None)
    dispensed_at: datetime = Field(...)
    notes: str | None = Field(None)
    reversal_of_id: UUID | None = Field(None)
    reason: str | None = Field(None)
    created_at: datetime = Field(...)


class DispenseResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    event_id: UUID = Field(...)
    prescription_item_id: UUID = Field(...)
    quantity: float = Field(...)
    quantity_unit: str = Field(...)


class DispenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    event: DispenseResponseEvent = Field(...)
    items: list[DispenseResponseItems] = Field(...)


class OwnDispensingResponseItemsItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    event_id: UUID = Field(...)
    prescription_item_id: UUID = Field(...)
    quantity: float = Field(...)
    quantity_unit: str = Field(...)


class OwnDispensingResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_reference: UUID = Field(...)
    organization_id: UUID = Field(...)
    dispensed_at: datetime = Field(...)
    reversal_of_id: UUID | None = Field(None)
    items: list[OwnDispensingResponseItemsItems] = Field(...)


class OwnDispensingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[OwnDispensingResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)


class PatientDispensingResponseItemsEvent(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    pharmacist_user_id: UUID = Field(...)
    organization_id: UUID = Field(...)
    share_id: UUID | None = Field(None)
    dispensed_at: datetime = Field(...)
    notes: str | None = Field(None)
    reversal_of_id: UUID | None = Field(None)
    reason: str | None = Field(None)
    created_at: datetime = Field(...)


class PatientDispensingResponseItemsItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    event_id: UUID = Field(...)
    prescription_item_id: UUID = Field(...)
    quantity: float = Field(...)
    quantity_unit: str = Field(...)


class PatientDispensingResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    event: PatientDispensingResponseItemsEvent = Field(...)
    items: list[PatientDispensingResponseItemsItems] = Field(...)


class PatientDispensingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[PatientDispensingResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)


class ReverseDispensingInput(InputModel):
    reason: str = Field(..., min_length=1, max_length=1000)


class ReverseDispensingResponseEvent(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_id: UUID = Field(...)
    pharmacist_user_id: UUID = Field(...)
    organization_id: UUID = Field(...)
    share_id: UUID | None = Field(None)
    dispensed_at: datetime = Field(...)
    notes: str | None = Field(None)
    reversal_of_id: UUID | None = Field(None)
    reason: str | None = Field(None)
    created_at: datetime = Field(...)


class ReverseDispensingResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    event_id: UUID = Field(...)
    prescription_item_id: UUID = Field(...)
    quantity: float = Field(...)
    quantity_unit: str = Field(...)


class ReverseDispensingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    event: ReverseDispensingResponseEvent = Field(...)
    items: list[ReverseDispensingResponseItems] = Field(...)
