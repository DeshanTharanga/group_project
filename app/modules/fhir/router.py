"""Thin async HTTP routes. Domain services own permissions and state transitions."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request

from app.core.security import Context, context
from app.modules.fhir import schemas as s
from app.modules.fhir import service
from app.services.common import invoke

router = APIRouter()


@router.get(
    "/fhir/r4/Patient/{patient_id}",
    tags=["FHIR export"],
    status_code=200,
    response_model=s.FhirPatientResponse,
)
async def fhir_patient(
    request: Request, ctx: Annotated[Context, Depends(context)], patient_id: UUID
):
    result = await invoke(
        ctx,
        "fhir_patient",
        service.fhir_patient,
        None,
        params={"patient_id": patient_id},
        response_model=s.FhirPatientResponse,
        status=200,
        idempotent=False,
    )
    return result


@router.get(
    "/fhir/r4/MedicationRequest/{item_id}",
    tags=["FHIR export"],
    status_code=200,
    response_model=s.FhirMedicationRequestResponse,
)
async def fhir_medication_request(
    request: Request, ctx: Annotated[Context, Depends(context)], item_id: UUID
):
    result = await invoke(
        ctx,
        "fhir_medication_request",
        service.fhir_medication_request,
        None,
        params={"item_id": item_id},
        response_model=s.FhirMedicationRequestResponse,
        status=200,
        idempotent=False,
    )
    return result
