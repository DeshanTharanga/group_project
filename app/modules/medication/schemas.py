"""Typed interface transcribed from the supplied Developer Guide. Extra inputs are rejected."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from app.core.schemas import InputModel


class CreateScheduleInput(InputModel):
    prescription_item_id: UUID = Field(...)
    timezone: str = Field(...)
    starts_at: AwareDatetime = Field(...)
    ends_at: AwareDatetime | None = Field(None)
    times: list[str] = Field(..., min_length=1)
    confirmed: Literal[True] = Field(...)


class CreateScheduleResponseSchedule(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_item_id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    timezone: str = Field(...)
    starts_at: datetime = Field(...)
    ends_at: datetime | None = Field(None)
    confirmed_at: datetime = Field(...)
    status: str = Field(...)
    created_at: datetime = Field(...)
    version: int = Field(...)


class CreateScheduleResponseTimes(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    schedule_id: UUID = Field(...)
    time_of_day: str = Field(...)


class CreateScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    schedule: CreateScheduleResponseSchedule = Field(...)
    times: list[CreateScheduleResponseTimes] = Field(...)


class ListSchedulesResponseItemsSchedule(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_item_id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    timezone: str = Field(...)
    starts_at: datetime = Field(...)
    ends_at: datetime | None = Field(None)
    confirmed_at: datetime = Field(...)
    status: str = Field(...)
    created_at: datetime = Field(...)
    version: int = Field(...)


class ListSchedulesResponseItemsTimes(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    schedule_id: UUID = Field(...)
    time_of_day: str = Field(...)


class ListSchedulesResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    schedule: ListSchedulesResponseItemsSchedule = Field(...)
    times: list[ListSchedulesResponseItemsTimes] = Field(...)


class ListSchedulesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[ListSchedulesResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)


class ScheduleStatusInput(InputModel):
    status: Literal["active", "paused", "completed", "cancelled"] = Field(...)
    reason: str = Field(..., min_length=1, max_length=1000)


class ScheduleStatusResponseSchedule(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_item_id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    timezone: str = Field(...)
    starts_at: datetime = Field(...)
    ends_at: datetime | None = Field(None)
    confirmed_at: datetime = Field(...)
    status: str = Field(...)
    created_at: datetime = Field(...)
    version: int = Field(...)


class ScheduleStatusResponseTimes(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    schedule_id: UUID = Field(...)
    time_of_day: str = Field(...)


class ScheduleStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    schedule: ScheduleStatusResponseSchedule = Field(...)
    times: list[ScheduleStatusResponseTimes] = Field(...)


class ReplaceScheduleInput(InputModel):
    prescription_item_id: UUID = Field(...)
    timezone: str = Field(...)
    starts_at: AwareDatetime = Field(...)
    ends_at: AwareDatetime | None = Field(None)
    times: list[str] = Field(..., min_length=1)
    confirmed: Literal[True] = Field(...)


class ReplaceScheduleResponseSchedule(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    prescription_item_id: UUID = Field(...)
    patient_user_id: UUID = Field(...)
    timezone: str = Field(...)
    starts_at: datetime = Field(...)
    ends_at: datetime | None = Field(None)
    confirmed_at: datetime = Field(...)
    status: str = Field(...)
    created_at: datetime = Field(...)
    version: int = Field(...)


class ReplaceScheduleResponseTimes(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    schedule_id: UUID = Field(...)
    time_of_day: str = Field(...)


class ReplaceScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    schedule: ReplaceScheduleResponseSchedule = Field(...)
    times: list[ReplaceScheduleResponseTimes] = Field(...)


class ListOccurrencesResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    schedule_id: UUID = Field(...)
    scheduled_for: datetime = Field(...)
    status: str = Field(...)
    snoozed_until: datetime | None = Field(None)
    created_at: datetime = Field(...)


class ListOccurrencesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[ListOccurrencesResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)


class SnoozeOccurrenceInput(InputModel):
    snoozed_until: AwareDatetime = Field(...)


class SnoozeOccurrenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    schedule_id: UUID = Field(...)
    scheduled_for: datetime = Field(...)
    status: str = Field(...)
    snoozed_until: datetime | None = Field(None)
    created_at: datetime = Field(...)


class RespondOccurrenceInput(InputModel):
    response: Literal["taken", "skipped"] = Field(...)
    reported_taken_at: AwareDatetime | None = Field(None)


class RespondOccurrenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    dose_occurrence_id: UUID = Field(...)
    response: str = Field(...)
    reported_taken_at: datetime | None = Field(None)
    recorded_by: UUID = Field(...)
    recorded_at: datetime = Field(...)
    correction_of_id: UUID | None = Field(None)
    correction_reason: str | None = Field(None)


class ListResponsesResponseItems(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    dose_occurrence_id: UUID = Field(...)
    response: str = Field(...)
    reported_taken_at: datetime | None = Field(None)
    recorded_by: UUID = Field(...)
    recorded_at: datetime = Field(...)
    correction_of_id: UUID | None = Field(None)
    correction_reason: str | None = Field(None)


class ListResponsesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[ListResponsesResponseItems] = Field(...)
    page: int = Field(...)
    page_size: int = Field(...)
    total: int = Field(...)


class CorrectLogInput(InputModel):
    response: Literal["taken", "skipped"] = Field(...)
    reported_taken_at: AwareDatetime | None = Field(None)
    correction_reason: str = Field(..., min_length=1, max_length=1000)


class CorrectLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(...)
    dose_occurrence_id: UUID = Field(...)
    response: str = Field(...)
    reported_taken_at: datetime | None = Field(None)
    recorded_by: UUID = Field(...)
    recorded_at: datetime = Field(...)
    correction_of_id: UUID | None = Field(None)
    correction_reason: str | None = Field(None)


class AdherenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    period_from: datetime = Field(...)
    period_to: datetime = Field(...)
    taken: int = Field(...)
    skipped: int = Field(...)
    unreported: int = Field(...)
    eligible: int = Field(...)
    percentage: float | None = Field(...)
    label: str = Field(...)
