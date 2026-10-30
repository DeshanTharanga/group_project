"""Shared validation: trim strings, reject unknown fields and non-finite numbers."""

from pydantic import BaseModel, ConfigDict, model_validator


class InputModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, allow_inf_nan=False)

    @model_validator(mode="after")
    def reject_null_required(self):
        # Optional inputs are omitted; only nullable domain fields may be cleared.
        nullable = {
            "phone",
            "registration_number",
            "qualifications",
            "specialty",
            "emergency_contact_name",
            "emergency_contact_phone",
            "notes",
            "next_dose_on",
            "claimed_prescriber",
            "starts_on",
            "ends_on",
            "medicine_id",
            "duration_days",
            "instructions",
            "route",
            "quantity",
            "quantity_unit",
            "original_document_id",
            "clinical_code",
            "description",
            "reported_taken_at",
            "ends_at",
            "organization_id",
            "consultation_id",
            "upload_request_id",
            "verification_application_id",
            "supersedes_id",
            "report_date",
            "lab_reference",
            "replacement_record_id",
            "summary",
        }
        for name in self.model_fields_set:
            if getattr(self, name) is None and name not in nullable:
                raise ValueError(f"{name} cannot be null; omit it when unused.")
        return self
