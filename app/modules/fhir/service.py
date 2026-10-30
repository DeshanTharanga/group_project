"""Limited read-only FHIR R4 projections; this is not a general FHIR server."""

from app.core.errors import require
from app.database import models as m
from app.services.common import get, patient_access


async def fhir_patient(ctx, data, patient_id):
    await patient_access(ctx, patient_id, "history_allergies")
    user = await get(ctx, m.User, patient_id)
    profile = await get(ctx, m.PatientProfile, patient_id)
    return {
        "resourceType": "Patient",
        "id": str(patient_id),
        "identifier": [{"system": "urn:medilink:patient", "value": str(patient_id)}],
        "name": [{"text": user.display_name}],
        "birthDate": profile.date_of_birth,
    }


async def fhir_medication_request(ctx, data, item_id):
    item = await get(ctx, m.PrescriptionItem, item_id)
    p = await get(ctx, m.Prescription, item.prescription_id)
    await patient_access(ctx, p.patient_user_id, "prescriptions")
    require(
        p.source == "doctor" and p.issued_at is not None,
        "Only issued doctor orders are exported.",
        404,
        "NOT_FOUND",
    )
    statuses = {
        "active": "active",
        "completed": "completed",
        "discontinued": "stopped",
        "cancelled": "cancelled",
        "superseded": "stopped",
    }
    return {
        "resourceType": "MedicationRequest",
        "id": str(item.id),
        "status": statuses[p.status],
        "intent": "order",
        "subject": {"reference": f"Patient/{p.patient_user_id}"},
        "medicationCodeableConcept": {"text": item.medicine_name_snapshot},
        "authoredOn": p.issued_at,
        "dosageInstruction": [
            {"text": "; ".join(v for v in (item.dose_text, item.frequency, item.instructions) if v)}
        ],
    }
