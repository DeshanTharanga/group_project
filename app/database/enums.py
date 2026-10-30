"""Initial enum labels inferred from the supplied API guide; see docs/implementation.md."""

from sqlalchemy.dialects.postgresql import ENUM

account_status = ENUM(
    "pending",
    "active",
    "suspended",
    "disabled",
    name="account_status",
    create_type=False,
    validate_strings=True,
)
professional_role = ENUM(
    "doctor",
    "pharmacist",
    "lab_staff",
    name="professional_role",
    create_type=False,
    validate_strings=True,
)
verification_status = ENUM(
    "not_submitted",
    "pending",
    "approved",
    "rejected",
    "more_info_requested",
    "suspended",
    name="verification_status",
    create_type=False,
    validate_strings=True,
)
grant_status = ENUM(
    "active", "revoked", "expired", name="grant_status", create_type=False, validate_strings=True
)
grant_category = ENUM(
    "history_allergies",
    "prescriptions",
    "reports",
    "measurements_vaccinations",
    "adherence",
    name="grant_category",
    create_type=False,
    validate_strings=True,
)
record_source = ENUM(
    "patient",
    "doctor",
    "laboratory",
    "integration",
    name="record_source",
    create_type=False,
    validate_strings=True,
)
clinical_record_status = ENUM(
    "active",
    "superseded",
    "withdrawn",
    name="clinical_record_status",
    create_type=False,
    validate_strings=True,
)
idempotency_actor_type = ENUM(
    "user", "client", name="idempotency_actor_type", create_type=False, validate_strings=True
)
document_status = ENUM(
    "active",
    "superseded",
    "withdrawn",
    name="document_status",
    create_type=False,
    validate_strings=True,
)
dose_status = ENUM(
    "upcoming",
    "due",
    "taken",
    "skipped",
    "unreported",
    "cancelled",
    name="dose_status",
    create_type=False,
    validate_strings=True,
)
dose_response = ENUM(
    "taken", "skipped", name="dose_response", create_type=False, validate_strings=True
)
entity_status = ENUM(
    "pending",
    "active",
    "suspended",
    "rejected",
    "inactive",
    name="entity_status",
    create_type=False,
    validate_strings=True,
)
integration_status = ENUM(
    "pending",
    "active",
    "suspended",
    "revoked",
    name="integration_status",
    create_type=False,
    validate_strings=True,
)
submission_status = ENUM(
    "received",
    "accepted",
    "rejected",
    "failed",
    name="submission_status",
    create_type=False,
    validate_strings=True,
)
upload_request_status = ENUM(
    "active",
    "used",
    "revoked",
    "expired",
    name="upload_request_status",
    create_type=False,
    validate_strings=True,
)
measurement_type = ENUM(
    "weight",
    "blood_pressure",
    "blood_glucose",
    name="measurement_type",
    create_type=False,
    validate_strings=True,
)
measurement_status = ENUM(
    "active",
    "superseded",
    "withdrawn",
    name="measurement_status",
    create_type=False,
    validate_strings=True,
)
schedule_status = ENUM(
    "active",
    "paused",
    "completed",
    "cancelled",
    name="schedule_status",
    create_type=False,
    validate_strings=True,
)
prescription_ocr_job_status = ENUM(
    "queued",
    "processing",
    "ready_for_review",
    "failed",
    "draft_created",
    name="prescription_ocr_job_status",
    create_type=False,
    validate_strings=True,
)
prescription_review_status = ENUM(
    "not_reviewed",
    "reviewed",
    "needs_clarification",
    "not_accepted",
    name="prescription_review_status",
    create_type=False,
    validate_strings=True,
)
review_outcome = ENUM(
    "reviewed",
    "needs_clarification",
    "not_accepted",
    name="review_outcome",
    create_type=False,
    validate_strings=True,
)
prescription_source = ENUM(
    "patient", "doctor", name="prescription_source", create_type=False, validate_strings=True
)
prescription_status = ENUM(
    "draft",
    "active",
    "completed",
    "discontinued",
    "cancelled",
    "superseded",
    name="prescription_status",
    create_type=False,
    validate_strings=True,
)
prescription_template_type = ENUM(
    "favourite",
    "template",
    name="prescription_template_type",
    create_type=False,
    validate_strings=True,
)
prescription_template_status = ENUM(
    "active",
    "archived",
    name="prescription_template_status",
    create_type=False,
    validate_strings=True,
)
share_status = ENUM(
    "created",
    "claimed",
    "confirmed",
    "expired",
    "revoked",
    name="share_status",
    create_type=False,
    validate_strings=True,
)
report_status = ENUM(
    "active",
    "superseded",
    "withdrawn",
    name="report_status",
    create_type=False,
    validate_strings=True,
)
organization_type = ENUM(
    "clinic",
    "hospital",
    "pharmacy",
    "laboratory",
    "other",
    name="organization_type",
    create_type=False,
    validate_strings=True,
)
