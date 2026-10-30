"""PostgreSQL models mapped from the supplied ER diagram."""

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    PrimaryKeyConstraint,
    SmallInteger,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.database import enums
from app.database.base import Base


class Medicine(Base):
    __tablename__ = "medicines"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="medicines_pkey"),
        Index("ix_medicines_generic_name", text("lower(generic_name)")),
        Index("ix_medicines_brand_name", text("lower(brand_name)")),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    generic_name = Column(Text, nullable=False)
    brand_name = Column(Text, nullable=True)
    strength = Column(Text, nullable=True)
    form = Column(Text, nullable=True)
    is_sample = Column(Boolean, server_default=text("true"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)


class PrescriptionItem(Base):
    __tablename__ = "prescription_items"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="prescription_items_pkey"),
        Index("ix_prescription_items_prescription", "prescription_id"),
        CheckConstraint("(duration_days IS NULL) OR (duration_days > 0)", name="ck_item_duration"),
        CheckConstraint("(quantity IS NULL) OR (quantity > (0)::numeric)", name="ck_item_quantity"),
        CheckConstraint(
            "(quantity IS NULL) = (quantity_unit IS NULL)", name="ck_item_quantity_unit"
        ),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    prescription_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "prescriptions.id", name="prescription_items_prescription_id_fkey", ondelete="RESTRICT"
        ),
        nullable=False,
    )
    medicine_id = Column(
        UUID(as_uuid=True),
        ForeignKey("medicines.id", name="prescription_items_medicine_id_fkey", ondelete="RESTRICT"),
        nullable=True,
    )
    medicine_name_snapshot = Column(Text, nullable=False)
    dose_text = Column(Text, nullable=False)
    route = Column(Text, nullable=True)
    frequency = Column(Text, nullable=False)
    duration_days = Column(Integer, nullable=True)
    instructions = Column(Text, nullable=True)
    quantity = Column(Numeric(12, 3), nullable=True)
    quantity_unit = Column(Text, nullable=True)
    is_prn = Column(Boolean, server_default=text("false"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)


class PrescriptionOCRJob(Base):
    __tablename__ = "prescription_ocr_jobs"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="prescription_ocr_jobs_pkey"),
        UniqueConstraint(
            "resulting_prescription_id", name="prescription_ocr_jobs_resulting_prescription_id_key"
        ),
        UniqueConstraint(
            "patient_user_id", "original_document_id", name="uq_prescription_ocr_patient_document"
        ),
        Index("ix_prescription_ocr_patient_created", "patient_user_id", "created_at"),
        Index("ix_prescription_ocr_status_created", "status", "created_at"),
        CheckConstraint("attempt_count >= 0", name="ck_prescription_ocr_attempts"),
        CheckConstraint(
            "(resulting_prescription_id IS NULL) = (status <> "
            "'draft_created'::prescription_ocr_job_status)",
            name="ck_prescription_ocr_draft_state",
        ),
        CheckConstraint(
            "(extracted_fields IS NULL) OR (jsonb_typeof(extracted_fields) = 'object'::text)",
            name="ck_prescription_ocr_extracted_object",
        ),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    patient_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "patient_profiles.user_id",
            name="prescription_ocr_jobs_patient_user_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    original_document_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "documents.id",
            name="prescription_ocr_jobs_original_document_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    requested_by_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id", name="prescription_ocr_jobs_requested_by_user_id_fkey", ondelete="RESTRICT"
        ),
        nullable=False,
    )
    status = Column(
        enums.prescription_ocr_job_status,
        server_default=text("'queued'::prescription_ocr_job_status"),
        nullable=False,
    )
    extracted_fields = Column(JSONB, nullable=True)
    attempt_count = Column(Integer, server_default=text("0"), nullable=False)
    error_code = Column(Text, nullable=True)
    resulting_prescription_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "prescriptions.id",
            name="prescription_ocr_jobs_resulting_prescription_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=text("now()"),
        onupdate=text("now()"),
        nullable=False,
    )


class PrescriptionReview(Base):
    __tablename__ = "prescription_reviews"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="prescription_reviews_pkey"),
        Index("ix_prescription_reviews_history", "prescription_id", "reviewed_at"),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    prescription_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "prescriptions.id",
            name="prescription_reviews_prescription_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    reviewer_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id", name="prescription_reviews_reviewer_user_id_fkey", ondelete="RESTRICT"
        ),
        nullable=False,
    )
    outcome = Column(enums.review_outcome, nullable=False)
    notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)


class PrescriptionTemplateItem(Base):
    __tablename__ = "prescription_template_items"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="prescription_template_items_pkey"),
        UniqueConstraint("template_id", "position", name="uq_prescription_template_item_position"),
        Index("ix_prescription_template_items_template", "template_id", "position"),
        CheckConstraint(
            "(duration_days IS NULL) OR (duration_days > 0)",
            name="ck_prescription_template_item_duration",
        ),
        CheckConstraint('"position" > 0', name="ck_prescription_template_item_position"),
        CheckConstraint(
            "(quantity IS NULL) OR (quantity > (0)::numeric)",
            name="ck_prescription_template_item_quantity",
        ),
        CheckConstraint(
            "(quantity IS NULL) = (quantity_unit IS NULL)",
            name="ck_prescription_template_item_quantity_unit",
        ),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    template_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "prescription_templates.id",
            name="prescription_template_items_template_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    position = Column(SmallInteger, nullable=False)
    medicine_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "medicines.id", name="prescription_template_items_medicine_id_fkey", ondelete="RESTRICT"
        ),
        nullable=True,
    )
    medicine_name_snapshot = Column(Text, nullable=False)
    dose_text = Column(Text, nullable=False)
    route = Column(Text, nullable=True)
    frequency = Column(Text, nullable=False)
    duration_days = Column(Integer, nullable=True)
    instructions = Column(Text, nullable=True)
    quantity = Column(Numeric(12, 3), nullable=True)
    quantity_unit = Column(Text, nullable=True)
    is_prn = Column(Boolean, server_default=text("false"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)


class PrescriptionTemplate(Base):
    __tablename__ = "prescription_templates"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="prescription_templates_pkey"),
        Index(
            "uq_prescription_template_active_name",
            "doctor_user_id",
            text("lower(name)"),
            unique=True,
            postgresql_where=text("status = 'active'"),
        ),
        Index("ix_prescription_templates_owner_status", "doctor_user_id", "status", "created_at"),
        CheckConstraint(
            "(status = 'archived'::prescription_template_status) = (archived_at IS NOT NULL)",
            name="ck_prescription_template_archive",
        ),
        CheckConstraint(
            "(length(btrim(name)) >= 1) AND (length(btrim(name)) <= 120)",
            name="ck_prescription_template_name",
        ),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    doctor_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id", name="prescription_templates_doctor_user_id_fkey", ondelete="RESTRICT"
        ),
        nullable=False,
    )
    name = Column(Text, nullable=False)
    template_type = Column(enums.prescription_template_type, nullable=False)
    status = Column(
        enums.prescription_template_status,
        server_default=text("'active'::prescription_template_status"),
        nullable=False,
    )
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=text("now()"),
        onupdate=text("now()"),
        nullable=False,
    )
    archived_at = Column(DateTime(timezone=True), nullable=True)


class Prescription(Base):
    __tablename__ = "prescriptions"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="prescriptions_pkey"),
        Index("ix_prescriptions_patient_status", "patient_user_id", "status", "created_at"),
        Index("ix_prescriptions_prescriber", "prescriber_user_id", "created_at"),
        CheckConstraint(
            "(ends_on IS NULL) OR (starts_on IS NULL) OR (ends_on >= starts_on)",
            name="ck_prescription_dates",
        ),
        CheckConstraint(
            "(status <> ALL (ARRAY['active'::prescription_status, "
            "'completed'::prescription_status, "
            "'discontinued'::prescription_status, "
            "'cancelled'::prescription_status, "
            "'superseded'::prescription_status])) OR (issued_at IS NOT NULL)",
            name="ck_prescription_issue_time",
        ),
        CheckConstraint(
            "(source <> 'doctor'::prescription_source) OR (prescriber_user_id IS NOT NULL)",
            name="ck_prescription_issuer",
        ),
        CheckConstraint(
            "(reviewed_by IS NULL) = (reviewed_at IS NULL)", name="ck_prescription_review_pair"
        ),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    patient_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "patient_profiles.user_id",
            name="prescriptions_patient_user_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    consultation_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "consultations.id", name="prescriptions_consultation_id_fkey", ondelete="RESTRICT"
        ),
        nullable=True,
    )
    prescriber_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", name="prescriptions_prescriber_user_id_fkey", ondelete="RESTRICT"),
        nullable=True,
    )
    source = Column(enums.prescription_source, nullable=False)
    claimed_prescriber = Column(Text, nullable=True)
    review_status = Column(
        enums.prescription_review_status,
        server_default=text("'not_reviewed'::prescription_review_status"),
        nullable=False,
    )
    reviewed_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", name="prescriptions_reviewed_by_fkey", ondelete="RESTRICT"),
        nullable=True,
    )
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(
        enums.prescription_status,
        server_default=text("'draft'::prescription_status"),
        nullable=False,
    )
    issued_at = Column(DateTime(timezone=True), nullable=True)
    starts_on = Column(Date, nullable=True)
    ends_on = Column(Date, nullable=True)
    previous_prescription_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "prescriptions.id",
            name="prescriptions_previous_prescription_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    original_document_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "documents.id", name="prescriptions_original_document_id_fkey", ondelete="RESTRICT"
        ),
        nullable=True,
    )
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", name="prescriptions_created_by_fkey", ondelete="RESTRICT"),
        nullable=False,
    )
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=text("now()"),
        onupdate=text("now()"),
        nullable=False,
    )
    version = Column(Integer, server_default=text("1"), nullable=False)
    status_reason = Column(Text, nullable=True)
