"""Typed interface transcribed from the supplied Developer Guide. Extra inputs are rejected."""

from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from app.core.schemas import InputModel


class ListMeasurementsResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    type: str = Field(...)
    value: float | None = Field(None)
    secondary_value: float | None = Field(None)
    unit: str = Field(...)
    measured_at: datetime = Field(...)
    recorded_by: UUID = Field(...)
    source: str = Field(...)
    notes: str | None = Field(None)
    status: str = Field(...)
    supersedes_id: UUID | None = Field(None)
    correction_reason: str | None = Field(None)
    created_at: datetime = Field(...)


class ListMeasurementsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[ListMeasurementsResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)


class CreateMeasurementInput(InputModel):
    consultation_id: UUID | None = Field(None)
    type: Literal["weight", "blood_pressure", "blood_glucose"] = Field(...)
    value: Decimal = Field(..., gt=0, allow_inf_nan=False, max_digits=12, decimal_places=4)
    secondary_value: Decimal | None = Field(
        None, gt=0, allow_inf_nan=False, max_digits=12, decimal_places=4
    )
    unit: Literal["kg", "lb", "mmol/L", "mg/dL", "mmHg"] = Field(...)
    measured_at: AwareDatetime = Field(...)
    notes: str | None = Field(None, max_length=2000)


class CreateMeasurementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    type: str = Field(...)
    value: float | None = Field(None)
    secondary_value: float | None = Field(None)
    unit: str = Field(...)
    measured_at: datetime = Field(...)
    recorded_by: UUID = Field(...)
    source: str = Field(...)
    notes: str | None = Field(None)
    status: str = Field(...)
    supersedes_id: UUID | None = Field(None)
    correction_reason: str | None = Field(None)
    created_at: datetime = Field(...)
