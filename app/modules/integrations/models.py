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
from sqlalchemy.dialects.postgresql import ARRAY, UUID

from app.database import enums
from app.database.base import Base


class IntegrationClient(Base):
    __tablename__ = "integration_clients"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="integration_clients_pkey"),
        UniqueConstraint("credential_hash", name="integration_clients_credential_hash_key"),
        Index("ix_integration_clients_org_status", "organization_id", "status", "expires_at"),
        CheckConstraint(
            "(status = 'revoked'::integration_status) = (revoked_at IS NOT NULL)",
            name="ck_integration_revoked",
        ),
        CheckConstraint("scopes <@ ARRAY['reports:write'::text]", name="ck_integration_scope"),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "organizations.id", name="integration_clients_organization_id_fkey", ondelete="RESTRICT"
        ),
        nullable=False,
    )
    name = Column(Text, nullable=False)
    credential_hash = Column(Text, nullable=False)
    scopes = Column(ARRAY(Text), server_default=text("ARRAY[]::text[]"), nullable=False)
    status = Column(
        enums.integration_status,
        server_default=text("'pending'::integration_status"),
        nullable=False,
    )
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", name="integration_clients_created_by_fkey", ondelete="RESTRICT"),
        nullable=False,
    )
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)


class IntegrationSubmission(Base):
    __tablename__ = "integration_submissions"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="integration_submissions_pkey"),
        UniqueConstraint("client_id", "idempotency_key", name="uq_integration_idempotency"),
        Index("ix_integration_submissions_status", "status", "received_at"),
        Index("uq_integration_external_report", "client_id", "external_report_id", unique=True),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    client_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "integration_clients.id",
            name="integration_submissions_client_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    upload_request_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "lab_upload_requests.id",
            name="integration_submissions_upload_request_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    external_report_id = Column(Text, nullable=False)
    idempotency_key = Column(Text, nullable=False)
    status = Column(
        enums.submission_status,
        server_default=text("'received'::submission_status"),
        nullable=False,
    )
    report_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "reports.id", name="integration_submissions_report_id_fkey", ondelete="RESTRICT"
        ),
        nullable=True,
    )
    received_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    error_code = Column(Text, nullable=True)
