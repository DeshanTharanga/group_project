"""Versioned REST routers. FHIR has its own root path."""

from fastapi import APIRouter

from app.modules.audit.router import router as audit
from app.modules.clinical_records.router import router as clinical_records
from app.modules.consent.router import router as consent
from app.modules.consultations.router import router as consultations
from app.modules.dispensing.router import router as dispensing
from app.modules.documents.router import router as documents
from app.modules.identity.router import router as identity
from app.modules.integrations.router import router as integrations
from app.modules.measurements.router import router as measurements
from app.modules.medication.router import router as medication
from app.modules.notifications.router import router as notifications
from app.modules.organizations.router import router as organizations
from app.modules.prescriptions.router import router as prescriptions
from app.modules.vaccinations.router import router as vaccinations
from app.modules.verification.router import router as verification

api_router = APIRouter()
for router in (
    identity,
    organizations,
    verification,
    consent,
    consultations,
    clinical_records,
    measurements,
    vaccinations,
    prescriptions,
    medication,
    dispensing,
    documents,
    notifications,
    audit,
    integrations,
):
    api_router.include_router(router)
