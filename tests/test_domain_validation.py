from datetime import UTC, datetime, timedelta
from decimal import Decimal
from io import BytesIO

import pytest
from PIL import Image
from pydantic import ValidationError

from app.core.errors import DomainError
from app.modules.documents.storage import detect
from app.modules.identity.schemas import OnboardInput, UpdateMeInput
from app.modules.measurements.service import validate_measurement
from app.modules.medication.schemas import CreateScheduleInput
from app.modules.medication.service import validate_response, validate_schedule


def test_public_onboarding_cannot_request_admin_or_source_fields():
    with pytest.raises(ValidationError):
        OnboardInput(display_name="Example", requested_role="super_admin")
    with pytest.raises(ValidationError):
        OnboardInput(display_name="Example", requested_role="patient", status="active")


def test_patch_omission_differs_from_clear():
    assert UpdateMeInput().model_dump(exclude_unset=True) == {}
    assert UpdateMeInput(phone=None).model_dump(exclude_unset=True) == {"phone": None}
    with pytest.raises(ValidationError):
        UpdateMeInput(display_name=None)
    with pytest.raises(ValidationError):
        UpdateMeInput(display_name="  ")


@pytest.mark.parametrize(
    "kind,unit,secondary",
    [
        ("weight", "mmHg", None),
        ("blood_pressure", "mmHg", None),
        ("blood_glucose", "kg", None),
        ("weight", "kg", 80),
    ],
)
def test_measurement_units_and_components(kind, unit, secondary):
    with pytest.raises(DomainError):
        validate_measurement(
            {"type": kind, "value": Decimal("80"), "secondary_value": secondary, "unit": unit}
        )


def schedule(**overrides):
    return {
        "prescription_item_id": "11111111-1111-4111-8111-111111111111",
        "timezone": "Asia/Colombo",
        "starts_at": datetime.now(UTC),
        "ends_at": None,
        "times": ["08:00", "20:00"],
        "confirmed": True,
        **overrides,
    }


def test_naive_schedule_timestamp_is_rejected():
    with pytest.raises(ValidationError):
        CreateScheduleInput(**schedule(starts_at="2026-10-30T08:00:00"))


@pytest.mark.parametrize(
    "overrides",
    [
        {"timezone": "Bad/Timezone"},
        {"times": ["08:00", "08:00"]},
        {"times": ["08:00:00+05:30"]},
        {"times": ["not-time"]},
        {"confirmed": False},
    ],
)
def test_schedule_rejects_ambiguous_or_unconfirmed_input(overrides):
    with pytest.raises(DomainError):
        validate_schedule(schedule(**overrides))


def test_taken_requires_time_and_skipped_forbids_it():
    with pytest.raises(DomainError):
        validate_response({"response": "taken"})
    with pytest.raises(DomainError):
        validate_response(
            {"response": "taken", "reported_taken_at": datetime.now(UTC) + timedelta(days=1)}
        )
    with pytest.raises(DomainError):
        validate_response({"response": "skipped", "reported_taken_at": datetime.now(UTC)})


def test_file_type_is_detected_from_content():
    b = BytesIO()
    Image.new("RGB", (2, 2)).save(b, format="PNG")
    assert detect(b.getvalue()) == "image/png"
    with pytest.raises(DomainError):
        detect(b"<script>fake.png</script>")
    with pytest.raises(DomainError):
        detect(b"%PDF-not-a-real-file")
