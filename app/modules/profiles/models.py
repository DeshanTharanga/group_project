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
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.database import enums
from app.database.base import Base


class PatientProfile(Base):
    __tablename__ = "patient_profiles"
    __table_args__ = (
        PrimaryKeyConstraint("user_id", name="patient_profiles_pkey"),
        CheckConstraint(
            "sex IN ('female', 'male', 'intersex', 'another', 'prefer_not_to_say')",
            name="ck_patient_sex",
        ),
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", name="patient_profiles_user_id_fkey", ondelete="RESTRICT"),
        nullable=False,
    )
    date_of_birth = Column(Date, nullable=False)
    sex = Column(Text, nullable=False)
    emergency_contact_name = Column(Text, nullable=True)
    emergency_contact_phone = Column(Text, nullable=True)
    notification_preferences = Column(JSONB, server_default=text("'{}'::jsonb"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=text("now()"),
        onupdate=text("now()"),
        nullable=False,
    )


class ProfessionalProfile(Base):
    __tablename__ = "professional_profiles"
    __table_args__ = (
        PrimaryKeyConstraint("user_id", name="professional_profiles_pkey"),
        UniqueConstraint("doctor_reference", name="professional_profiles_doctor_reference_key"),
        Index("ix_professional_registration", "role", "registration_number"),
        CheckConstraint(
            "(role = 'doctor'::professional_role) = (doctor_reference IS NOT NULL)",
            name="ck_doctor_reference_role",
        ),
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", name="professional_profiles_user_id_fkey", ondelete="RESTRICT"),
        nullable=False,
    )
    role = Column(enums.professional_role, nullable=False)
    doctor_reference = Column(Text, nullable=True)
    registration_number = Column(Text, nullable=True)
    qualifications = Column(Text, nullable=True)
    specialty = Column(Text, nullable=True)
    verification_status = Column(
        enums.verification_status,
        server_default=text("'not_submitted'::verification_status"),
        nullable=False,
    )
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=text("now()"),
        onupdate=text("now()"),
        nullable=False,
    )
