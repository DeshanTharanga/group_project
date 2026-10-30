"""Typed interface transcribed from the supplied Developer Guide. Extra inputs are rejected."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class FhirPatientResponseIdentifier(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    system: str = Field(...)
    value: str = Field(...)


class FhirPatientResponseName(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    text: str = Field(...)


class FhirPatientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    resourceType: str = Field(...)
    id: str = Field(...)
    identifier: list[FhirPatientResponseIdentifier] = Field(...)
    name: list[FhirPatientResponseName] = Field(...)
    birthDate: date | None = Field(None)


class FhirMedicationRequestResponseSubject(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    reference: str = Field(...)


class FhirMedicationRequestResponseMedicationcodeableconcept(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    text: str = Field(...)


class FhirMedicationRequestResponseDosageinstruction(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    text: str = Field(...)


class FhirMedicationRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    resourceType: str = Field(...)
    id: str = Field(...)
    status: str = Field(...)
    intent: str = Field(...)
    subject: FhirMedicationRequestResponseSubject = Field(...)
    medicationCodeableConcept: FhirMedicationRequestResponseMedicationcodeableconcept = Field(...)
    authoredOn: datetime = Field(...)
    dosageInstruction: list[FhirMedicationRequestResponseDosageinstruction] = Field(...)
