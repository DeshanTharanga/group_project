"""PostgreSQL models mapped from the supplied ER diagram."""

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    PrimaryKeyConstraint,
    Text,
    Time,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID

from app.database import enums
from app.database.base import Base


class DoseOccurrence(Base):
    __tablename__ = "dose_occurrences"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="dose_occurrences_pkey"),
        UniqueConstraint("schedule_id", "scheduled_for", name="uq_dose_occurrence"),
        Index("ix_dose_occurrences_due", "status", "scheduled_for"),
        Index("ix_dose_occurrences_schedule", "schedule_id", "scheduled_for"),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    schedule_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "medication_schedules.id", name="dose_occurrences_schedule_id_fkey", ondelete="RESTRICT"
        ),
        nullable=False,
    )
    scheduled_for = Column(DateTime(timezone=True), nullable=False)
    status = Column(
        enums.dose_status, server_default=text("'upcoming'::dose_status"), nullable=False
    )
    snoozed_until = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)


class MedicationLog(Base):
    __tablename__ = "medication_logs"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="medication_logs_pkey"),
        Index("ix_medication_logs_occurrence", "dose_occurrence_id", "recorded_at"),
        CheckConstraint(
            "(correction_of_id IS NULL) = (correction_reason IS NULL)",
            name="ck_medication_log_correction",
        ),
        CheckConstraint(
            "(response <> 'taken'::dose_response) OR (reported_taken_at IS NOT NULL)",
            name="ck_medication_log_taken_time",
        ),
        UniqueConstraint("correction_of_id", name="uq_log_single_correction"),
        Index(
            "uq_log_initial_response",
            "dose_occurrence_id",
            unique=True,
            postgresql_where=text("correction_of_id IS NULL"),
        ),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    dose_occurrence_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "dose_occurrences.id",
            name="medication_logs_dose_occurrence_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    response = Column(enums.dose_response, nullable=False)
    reported_taken_at = Column(DateTime(timezone=True), nullable=True)
    recorded_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", name="medication_logs_recorded_by_fkey", ondelete="RESTRICT"),
        nullable=False,
    )
    recorded_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    correction_of_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "medication_logs.id", name="medication_logs_correction_of_id_fkey", ondelete="RESTRICT"
        ),
        nullable=True,
    )
    correction_reason = Column(Text, nullable=True)


class MedicationSchedule(Base):
    __tablename__ = "medication_schedules"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="medication_schedules_pkey"),
        Index("ix_schedules_patient_status", "patient_user_id", "status", "starts_at"),
        Index("ix_schedules_item", "prescription_item_id"),
        CheckConstraint("(ends_at IS NULL) OR (ends_at >= starts_at)", name="ck_schedule_window"),
        Index(
            "uq_active_item_schedule",
            "prescription_item_id",
            unique=True,
            postgresql_where=text("status IN ('active', 'paused')"),
        ),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    prescription_item_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "prescription_items.id",
            name="medication_schedules_prescription_item_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    patient_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "patient_profiles.user_id",
            name="medication_schedules_patient_user_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    timezone = Column(Text, nullable=False)
    starts_at = Column(DateTime(timezone=True), nullable=False)
    ends_at = Column(DateTime(timezone=True), nullable=True)
    confirmed_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(
        enums.schedule_status, server_default=text("'active'::schedule_status"), nullable=False
    )
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    version = Column(Integer, server_default=text("1"), nullable=False)


class ScheduleTime(Base):
    __tablename__ = "schedule_times"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="schedule_times_pkey"),
        UniqueConstraint("schedule_id", "time_of_day", name="uq_schedule_time"),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    schedule_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "medication_schedules.id", name="schedule_times_schedule_id_fkey", ondelete="RESTRICT"
        ),
        nullable=False,
    )
    time_of_day = Column(Time, nullable=False)
