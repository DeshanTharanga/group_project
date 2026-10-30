"""PostgreSQL models mapped from the supplied ER diagram."""

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    PrimaryKeyConstraint,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID

from app.database import enums
from app.database.base import Base


class Allergy(Base):
    __tablename__ = "allergies"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="allergies_pkey"),
        Index("ix_allergies_patient_date", "patient_user_id", "recorded_at"),
        Index("ix_allergies_consultation", "consultation_id"),
        CheckConstraint(
            "(supersedes_id IS NULL) = (correction_reason IS NULL)", name="ck_allergy_correction"
        ),
        UniqueConstraint("supersedes_id", name="uq_allergies_replacement"),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    patient_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "patient_profiles.user_id", name="allergies_patient_user_id_fkey", ondelete="RESTRICT"
        ),
        nullable=False,
    )
    consultation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("consultations.id", name="allergies_consultation_id_fkey", ondelete="RESTRICT"),
        nullable=True,
    )
    allergen = Column(Text, nullable=False)
    reaction = Column(Text, nullable=True)
    severity = Column(Text, nullable=True)
    source = Column(enums.record_source, nullable=False)
    recorded_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", name="allergies_recorded_by_fkey", ondelete="RESTRICT"),
        nullable=False,
    )
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", name="allergies_organization_id_fkey", ondelete="RESTRICT"),
        nullable=True,
    )
    status = Column(
        enums.clinical_record_status,
        server_default=text("'active'::clinical_record_status"),
        nullable=False,
    )
    recorded_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    supersedes_id = Column(
        UUID(as_uuid=True),
        ForeignKey("allergies.id", name="allergies_supersedes_id_fkey", ondelete="RESTRICT"),
        nullable=True,
    )
    correction_reason = Column(Text, nullable=True)


class ClinicalNote(Base):
    __tablename__ = "clinical_notes"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="clinical_notes_pkey"),
        Index("ix_clinical_notes_patient_date", "patient_user_id", "recorded_at"),
        Index("ix_clinical_notes_consultation", "consultation_id"),
        CheckConstraint(
            "(supersedes_id IS NULL) = (correction_reason IS NULL)",
            name="ck_clinical_note_correction",
        ),
        UniqueConstraint("supersedes_id", name="uq_clinical_notes_replacement"),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    patient_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "patient_profiles.user_id",
            name="clinical_notes_patient_user_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    consultation_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "consultations.id", name="clinical_notes_consultation_id_fkey", ondelete="RESTRICT"
        ),
        nullable=True,
    )
    note_type = Column(Text, nullable=False)
    note_text = Column(Text, nullable=False)
    source = Column(enums.record_source, nullable=False)
    recorded_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", name="clinical_notes_recorded_by_fkey", ondelete="RESTRICT"),
        nullable=False,
    )
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "organizations.id", name="clinical_notes_organization_id_fkey", ondelete="RESTRICT"
        ),
        nullable=True,
    )
    status = Column(
        enums.clinical_record_status,
        server_default=text("'active'::clinical_record_status"),
        nullable=False,
    )
    recorded_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    supersedes_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "clinical_notes.id", name="clinical_notes_supersedes_id_fkey", ondelete="RESTRICT"
        ),
        nullable=True,
    )
    correction_reason = Column(Text, nullable=True)


class Condition(Base):
    __tablename__ = "conditions"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="conditions_pkey"),
        Index("ix_conditions_patient_date", "patient_user_id", "recorded_at"),
        Index("ix_conditions_consultation", "consultation_id"),
        CheckConstraint(
            "(supersedes_id IS NULL) = (correction_reason IS NULL)", name="ck_condition_correction"
        ),
        UniqueConstraint("supersedes_id", name="uq_conditions_replacement"),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    patient_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "patient_profiles.user_id", name="conditions_patient_user_id_fkey", ondelete="RESTRICT"
        ),
        nullable=False,
    )
    consultation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("consultations.id", name="conditions_consultation_id_fkey", ondelete="RESTRICT"),
        nullable=True,
    )
    condition_name = Column(Text, nullable=False)
    clinical_code = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    source = Column(enums.record_source, nullable=False)
    recorded_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", name="conditions_recorded_by_fkey", ondelete="RESTRICT"),
        nullable=False,
    )
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", name="conditions_organization_id_fkey", ondelete="RESTRICT"),
        nullable=True,
    )
    status = Column(
        enums.clinical_record_status,
        server_default=text("'active'::clinical_record_status"),
        nullable=False,
    )
    recorded_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    supersedes_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conditions.id", name="conditions_supersedes_id_fkey", ondelete="RESTRICT"),
        nullable=True,
    )
    correction_reason = Column(Text, nullable=True)


class Diagnosis(Base):
    __tablename__ = "diagnoses"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="diagnoses_pkey"),
        Index("ix_diagnoses_patient_date", "patient_user_id", "diagnosed_at"),
        Index("ix_diagnoses_consultation", "consultation_id"),
        CheckConstraint(
            "(supersedes_id IS NULL) = (correction_reason IS NULL)", name="ck_diagnosis_correction"
        ),
        UniqueConstraint("supersedes_id", name="uq_diagnoses_replacement"),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    patient_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "patient_profiles.user_id", name="diagnoses_patient_user_id_fkey", ondelete="RESTRICT"
        ),
        nullable=False,
    )
    consultation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("consultations.id", name="diagnoses_consultation_id_fkey", ondelete="RESTRICT"),
        nullable=True,
    )
    diagnosis_name = Column(Text, nullable=False)
    clinical_code = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    source = Column(enums.record_source, nullable=False)
    recorded_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", name="diagnoses_recorded_by_fkey", ondelete="RESTRICT"),
        nullable=False,
    )
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", name="diagnoses_organization_id_fkey", ondelete="RESTRICT"),
        nullable=True,
    )
    status = Column(
        enums.clinical_record_status,
        server_default=text("'active'::clinical_record_status"),
        nullable=False,
    )
    diagnosed_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    supersedes_id = Column(
        UUID(as_uuid=True),
        ForeignKey("diagnoses.id", name="diagnoses_supersedes_id_fkey", ondelete="RESTRICT"),
        nullable=True,
    )
    correction_reason = Column(Text, nullable=True)


class RecordCorrection(Base):
    __tablename__ = "record_corrections"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="record_corrections_pkey"),
        Index("ix_corrections_condition", "condition_id", "created_at"),
        Index("ix_corrections_diagnosis", "diagnosis_id", "created_at"),
        Index("ix_corrections_allergy", "allergy_id", "created_at"),
        Index("ix_corrections_note", "clinical_note_id", "created_at"),
        CheckConstraint(
            "num_nonnulls(condition_id, diagnosis_id, allergy_id, clinical_note_id) = 1",
            name="ck_correction_one_target",
        ),
        CheckConstraint(
            "(replacement_record_type IS NULL) = (replacement_record_id IS NULL)",
            name="ck_correction_replacement_pair",
        ),
        CheckConstraint(
            "request_status = ANY (ARRAY['open'::text, 'accepted'::text, "
            "'rejected'::text, 'resolved'::text])",
            name="ck_correction_status",
        ),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    condition_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "conditions.id", name="record_corrections_condition_id_fkey", ondelete="RESTRICT"
        ),
        nullable=True,
    )
    diagnosis_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "diagnoses.id", name="record_corrections_diagnosis_id_fkey", ondelete="RESTRICT"
        ),
        nullable=True,
    )
    allergy_id = Column(
        UUID(as_uuid=True),
        ForeignKey("allergies.id", name="record_corrections_allergy_id_fkey", ondelete="RESTRICT"),
        nullable=True,
    )
    clinical_note_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "clinical_notes.id",
            name="record_corrections_clinical_note_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    requested_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", name="record_corrections_requested_by_fkey", ondelete="RESTRICT"),
        nullable=False,
    )
    reason = Column(Text, nullable=False)
    request_status = Column(Text, server_default=text("'open'::text"), nullable=False)
    reviewed_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", name="record_corrections_reviewed_by_fkey", ondelete="RESTRICT"),
        nullable=True,
    )
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    resolution_reason = Column(Text, nullable=True)
    replacement_record_type = Column(Text, nullable=True)
    replacement_record_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
