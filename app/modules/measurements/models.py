"""PostgreSQL models mapped from the supplied ER diagram."""

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    PrimaryKeyConstraint,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID

from app.database import enums
from app.database.base import Base


class Measurement(Base):
    __tablename__ = "measurements"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="measurements_pkey"),
        Index("ix_measurements_patient_type_date", "patient_user_id", "type", "measured_at"),
        CheckConstraint(
            "(supersedes_id IS NULL) = (correction_reason IS NULL)",
            name="ck_measurement_correction",
        ),
        CheckConstraint(
            "(value IS NULL) OR (value > (0)::numeric)", name="ck_measurement_positive"
        ),
        CheckConstraint(
            "(secondary_value IS NULL) OR (secondary_value > (0)::numeric)",
            name="ck_measurement_secondary_positive",
        ),
        CheckConstraint(
            "((type = 'weight'::measurement_type) AND (unit = ANY "
            "(ARRAY['kg'::text, 'lb'::text]))) OR ((type = "
            "'blood_glucose'::measurement_type) AND (unit = ANY "
            "(ARRAY['mmol/L'::text, 'mg/dL'::text]))) OR ((type = "
            "'blood_pressure'::measurement_type) AND (unit = 'mmHg'::text))",
            name="ck_measurement_unit",
        ),
        CheckConstraint(
            "((type = 'blood_pressure'::measurement_type) AND (value IS NOT "
            "NULL) AND (secondary_value IS NOT NULL) AND (unit = "
            "'mmHg'::text)) OR ((type <> 'blood_pressure'::measurement_type) "
            "AND (value IS NOT NULL) AND (secondary_value IS NULL))",
            name="ck_measurement_values",
        ),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    patient_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "patient_profiles.user_id",
            name="measurements_patient_user_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    type = Column(enums.measurement_type, nullable=False)
    value = Column(Numeric(12, 4), nullable=True)
    secondary_value = Column(Numeric(12, 4), nullable=True)
    unit = Column(Text, nullable=False)
    measured_at = Column(DateTime(timezone=True), nullable=False)
    recorded_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", name="measurements_recorded_by_fkey", ondelete="RESTRICT"),
        nullable=False,
    )
    source = Column(enums.record_source, nullable=False)
    notes = Column(Text, nullable=True)
    status = Column(
        enums.measurement_status,
        server_default=text("'active'::measurement_status"),
        nullable=False,
    )
    supersedes_id = Column(
        UUID(as_uuid=True),
        ForeignKey("measurements.id", name="measurements_supersedes_id_fkey", ondelete="RESTRICT"),
        nullable=True,
    )
    correction_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
