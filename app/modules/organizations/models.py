"""PostgreSQL models mapped from the supplied ER diagram."""

from sqlalchemy import (
    Column,
    DateTime,
    FetchedValue,
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


class OrganizationMembership(Base):
    __tablename__ = "organization_memberships"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="organization_memberships_pkey"),
        UniqueConstraint("organization_id", "user_id", "role", name="uq_membership_org_user_role"),
        Index("ix_memberships_user_status", "user_id", "status"),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "organizations.id",
            name="organization_memberships_organization_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", name="organization_memberships_user_id_fkey", ondelete="RESTRICT"),
        nullable=False,
    )
    role = Column(enums.professional_role, nullable=False)
    status = Column(
        enums.verification_status,
        server_default=text("'pending'::verification_status"),
        nullable=False,
    )
    verified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)


class Organization(Base):
    __tablename__ = "organizations"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="organizations_pkey"),
        Index("ix_organizations_type_status", "type", "status"),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    name = Column(Text, nullable=False)
    type = Column(enums.organization_type, nullable=False)
    registration_ref = Column(Text, nullable=True)
    status = Column(
        enums.entity_status, server_default=text("'pending'::entity_status"), nullable=False
    )
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=text("now()"),
        onupdate=text("now()"),
        server_onupdate=FetchedValue(),
        nullable=False,
    )
