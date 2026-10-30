"""PostgreSQL models mapped from the supplied ER diagram."""

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    PrimaryKeyConstraint,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base


class Consultation(Base):
    __tablename__ = "consultations"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="consultations_pkey"),
        Index("ix_consultations_patient_date", "patient_user_id", "started_at"),
        Index("ix_consultations_doctor_date", "doctor_user_id", "started_at"),
        CheckConstraint(
            "(ended_at IS NULL) OR (ended_at >= started_at)", name="ck_consultation_window"
        ),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    patient_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "patient_profiles.user_id",
            name="consultations_patient_user_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    doctor_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", name="consultations_doctor_user_id_fkey", ondelete="RESTRICT"),
        nullable=False,
    )
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "organizations.id", name="consultations_organization_id_fkey", ondelete="RESTRICT"
        ),
        nullable=True,
    )
    grant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("access_grants.id", name="consultations_grant_id_fkey", ondelete="RESTRICT"),
        nullable=False,
    )
    started_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    summary = Column(Text, nullable=True)
