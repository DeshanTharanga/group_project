"""PostgreSQL models mapped from the supplied ER diagram."""

from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
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


class Vaccination(Base):
    __tablename__ = "vaccinations"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="vaccinations_pkey"),
        Index("ix_vaccinations_patient_date", "patient_user_id", "administered_on"),
        Index("ix_vaccinations_next_dose", "next_dose_on"),
        CheckConstraint(
            "(supersedes_id IS NULL) = (correction_reason IS NULL)", name="ck_vaccine_correction"
        ),
        CheckConstraint(
            "(next_dose_on IS NULL) OR (next_dose_on >= administered_on)",
            name="ck_vaccine_next_dose",
        ),
        UniqueConstraint("supersedes_id", name="uq_vaccinations_replacement"),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    patient_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "patient_profiles.user_id",
            name="vaccinations_patient_user_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    vaccine_name = Column(Text, nullable=False)
    administered_on = Column(Date, nullable=False)
    dose_details = Column(Text, nullable=True)
    next_dose_on = Column(Date, nullable=True)
    recorded_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", name="vaccinations_recorded_by_fkey", ondelete="RESTRICT"),
        nullable=False,
    )
    source = Column(enums.record_source, nullable=False)
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "organizations.id", name="vaccinations_organization_id_fkey", ondelete="RESTRICT"
        ),
        nullable=True,
    )
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    supersedes_id = Column(
        UUID(as_uuid=True),
        ForeignKey("vaccinations.id", name="vaccinations_supersedes_id_fkey", ondelete="RESTRICT"),
        nullable=True,
    )
    correction_reason = Column(Text, nullable=True)
