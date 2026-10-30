"""PostgreSQL models mapped from the supplied ER diagram."""

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    PrimaryKeyConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID

from app.database import enums
from app.database.base import Base


class AccessGrant(Base):
    __tablename__ = "access_grants"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="access_grants_pkey"),
        Index("ix_grants_patient_status_expiry", "patient_user_id", "status", "expires_at"),
        Index(
            "ix_grants_professional_status_expiry", "professional_user_id", "status", "expires_at"
        ),
        CheckConstraint(
            "(status = 'revoked'::grant_status) = (revoked_at IS NOT NULL)", name="ck_grant_revoked"
        ),
        CheckConstraint("expires_at > starts_at", name="ck_grant_window"),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    patient_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "patient_profiles.user_id",
            name="access_grants_patient_user_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    professional_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", name="access_grants_professional_user_id_fkey", ondelete="RESTRICT"),
        nullable=False,
    )
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "organizations.id", name="access_grants_organization_id_fkey", ondelete="RESTRICT"
        ),
        nullable=True,
    )
    allow_consultation = Column(Boolean, server_default=text("false"), nullable=False)
    status = Column(
        enums.grant_status, server_default=text("'active'::grant_status"), nullable=False
    )
    starts_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)


class GrantCategory(Base):
    __tablename__ = "grant_categories"
    __table_args__ = (PrimaryKeyConstraint("grant_id", "category", name="grant_categories_pkey"),)
    grant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("access_grants.id", name="grant_categories_grant_id_fkey", ondelete="RESTRICT"),
        nullable=False,
    )
    category = Column(enums.grant_category, nullable=False)
