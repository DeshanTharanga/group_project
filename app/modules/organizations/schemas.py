"""Typed interface transcribed from the supplied Developer Guide. Extra inputs are rejected."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.schemas import InputModel


class ListOrganizationsResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    name: str = Field(...)
    type: str = Field(...)


class ListOrganizationsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[ListOrganizationsResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)


class CreateOrganizationInput(InputModel):
    name: str = Field(..., min_length=1, max_length=200)
    type: Literal["clinic", "hospital", "pharmacy", "laboratory", "other"] = Field(...)
    registration_ref: str | None = Field(None, max_length=100)


class CreateOrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    name: str = Field(...)
    type: str = Field(...)
    registration_ref: str | None = Field(None)
    status: str = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)


class RequestMembershipInput(InputModel):
    organization_id: UUID = Field(...)
    role: Literal["doctor", "pharmacist", "lab_staff"] = Field(...)


class RequestMembershipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    organization_id: UUID = Field(...)
    user_id: UUID = Field(...)
    role: str = Field(...)
    status: str = Field(...)
    verified_at: datetime | None = Field(None)
    created_at: datetime = Field(...)


class DecideOrganizationInput(InputModel):
    status: Literal["active", "suspended", "rejected", "inactive"] = Field(...)
    reason: str = Field(..., min_length=1, max_length=1000)


class DecideOrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    name: str = Field(...)
    type: str = Field(...)
    registration_ref: str | None = Field(None)
    status: str = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)


class AdminOrganizationsResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    name: str = Field(...)
    type: str = Field(...)
    registration_ref: str | None = Field(None)
    status: str = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)


class AdminOrganizationsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[AdminOrganizationsResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)


class AdminMembershipsResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    organization_id: UUID = Field(...)
    user_id: UUID = Field(...)
    role: str = Field(...)
    status: str = Field(...)
    verified_at: datetime | None = Field(None)
    created_at: datetime = Field(...)


class AdminMembershipsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[AdminMembershipsResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)


class DecideMembershipInput(InputModel):
    status: Literal["approved", "rejected", "more_info_requested", "suspended"] = Field(...)
    reason: str = Field(..., min_length=1, max_length=1000)


class DecideMembershipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    organization_id: UUID = Field(...)
    user_id: UUID = Field(...)
    role: str = Field(...)
    status: str = Field(...)
    verified_at: datetime | None = Field(None)
    created_at: datetime = Field(...)
