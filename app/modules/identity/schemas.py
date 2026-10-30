"""Typed interface transcribed from the supplied Developer Guide. Extra inputs are rejected."""

from datetime import date, datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.schemas import InputModel


class OnboardInput(InputModel):
    display_name: str = Field(..., min_length=1, max_length=150)
    phone: str | None = Field(None, max_length=32)
    requested_role: Literal["patient", "doctor", "pharmacist", "lab_staff"] = Field(...)


class OnboardResponseUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    email: str | None = Field(None)
    display_name: str = Field(...)
    phone: str | None = Field(None)
    status: str = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)


class OnboardResponsePatientProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: UUID = Field(...)
    date_of_birth: date = Field(...)
    sex: str = Field(...)
    emergency_contact_name: str | None = Field(None)
    emergency_contact_phone: str | None = Field(None)
    notification_preferences: dict[str, Any] = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)


class OnboardResponseProfessionalProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: UUID = Field(...)
    role: str = Field(...)
    doctor_reference: str | None = Field(None)
    registration_number: str | None = Field(None)
    qualifications: str | None = Field(None)
    specialty: str | None = Field(None)
    verification_status: str = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)


class OnboardResponseMemberships(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    organization_id: UUID = Field(...)
    user_id: UUID = Field(...)
    role: str = Field(...)
    status: str = Field(...)
    verified_at: datetime | None = Field(None)
    created_at: datetime = Field(...)


class OnboardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user: OnboardResponseUser = Field(...)
    roles: list[str] = Field(...)
    patient_profile: OnboardResponsePatientProfile | None = Field(None)
    professional_profile: OnboardResponseProfessionalProfile | None = Field(None)
    memberships: list[OnboardResponseMemberships] = Field(...)


class MeResponseUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    email: str | None = Field(None)
    display_name: str = Field(...)
    phone: str | None = Field(None)
    status: str = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)


class MeResponsePatientProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: UUID = Field(...)
    date_of_birth: date = Field(...)
    sex: str = Field(...)
    emergency_contact_name: str | None = Field(None)
    emergency_contact_phone: str | None = Field(None)
    notification_preferences: dict[str, Any] = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)


class MeResponseProfessionalProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: UUID = Field(...)
    role: str = Field(...)
    doctor_reference: str | None = Field(None)
    registration_number: str | None = Field(None)
    qualifications: str | None = Field(None)
    specialty: str | None = Field(None)
    verification_status: str = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)


class MeResponseMemberships(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    organization_id: UUID = Field(...)
    user_id: UUID = Field(...)
    role: str = Field(...)
    status: str = Field(...)
    verified_at: datetime | None = Field(None)
    created_at: datetime = Field(...)


class MeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user: MeResponseUser = Field(...)
    roles: list[str] = Field(...)
    patient_profile: MeResponsePatientProfile | None = Field(None)
    professional_profile: MeResponseProfessionalProfile | None = Field(None)
    memberships: list[MeResponseMemberships] = Field(...)


class UpdateMeInput(InputModel):
    display_name: str | None = Field(None, min_length=1, max_length=150)
    phone: str | None = Field(None, max_length=32)


class UpdateMeResponseUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    email: str | None = Field(None)
    display_name: str = Field(...)
    phone: str | None = Field(None)
    status: str = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)


class UpdateMeResponsePatientProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: UUID = Field(...)
    date_of_birth: date = Field(...)
    sex: str = Field(...)
    emergency_contact_name: str | None = Field(None)
    emergency_contact_phone: str | None = Field(None)
    notification_preferences: dict[str, Any] = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)


class UpdateMeResponseProfessionalProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: UUID = Field(...)
    role: str = Field(...)
    doctor_reference: str | None = Field(None)
    registration_number: str | None = Field(None)
    qualifications: str | None = Field(None)
    specialty: str | None = Field(None)
    verification_status: str = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)


class UpdateMeResponseMemberships(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    organization_id: UUID = Field(...)
    user_id: UUID = Field(...)
    role: str = Field(...)
    status: str = Field(...)
    verified_at: datetime | None = Field(None)
    created_at: datetime = Field(...)


class UpdateMeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user: UpdateMeResponseUser = Field(...)
    roles: list[str] = Field(...)
    patient_profile: UpdateMeResponsePatientProfile | None = Field(None)
    professional_profile: UpdateMeResponseProfessionalProfile | None = Field(None)
    memberships: list[UpdateMeResponseMemberships] = Field(...)


class UpdatePatientProfileInputNotificationPreferences(InputModel):
    medication_in_app: bool | None = Field(None)
    vaccination_in_app: bool | None = Field(None)


class UpdatePatientProfileInput(InputModel):
    date_of_birth: date | None = Field(None)
    sex: Literal["female", "male", "intersex", "another", "prefer_not_to_say"] | None = Field(None)
    emergency_contact_name: str | None = Field(None, max_length=150)
    emergency_contact_phone: str | None = Field(None, max_length=32)
    notification_preferences: UpdatePatientProfileInputNotificationPreferences | None = Field(None)


class UpdatePatientProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: UUID = Field(...)
    date_of_birth: date = Field(...)
    sex: str = Field(...)
    emergency_contact_name: str | None = Field(None)
    emergency_contact_phone: str | None = Field(None)
    notification_preferences: dict[str, Any] = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)


class UpdateProfessionalProfileInput(InputModel):
    role: Literal["doctor", "pharmacist", "lab_staff"] = Field(...)
    registration_number: str | None = Field(None, max_length=100)
    qualifications: str | None = Field(None, max_length=2000)
    specialty: str | None = Field(None, max_length=150)


class UpdateProfessionalProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: UUID = Field(...)
    role: str = Field(...)
    doctor_reference: str | None = Field(None)
    registration_number: str | None = Field(None)
    qualifications: str | None = Field(None)
    specialty: str | None = Field(None)
    verification_status: str = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
