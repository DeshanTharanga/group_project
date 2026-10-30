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

from app.database import enums
from app.database.base import Base


class VerificationApplicationDocument(Base):
    __tablename__ = "verification_application_documents"
    __table_args__ = (
        PrimaryKeyConstraint(
            "application_id", "document_id", name="verification_application_documents_pkey"
        ),
        Index("ix_verification_application_documents_document", "document_id"),
    )
    application_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "verification_applications.id",
            name="verification_application_documents_application_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "documents.id",
            name="verification_application_documents_document_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    attached_by = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="verification_application_documents_attached_by_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    attached_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)


class VerificationApplication(Base):
    __tablename__ = "verification_applications"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="verification_applications_pkey"),
        Index("ix_verification_queue", "status", "submitted_at"),
        Index("ix_verification_user", "user_id", "submitted_at"),
        CheckConstraint(
            "(reviewed_by IS NULL) = (reviewed_at IS NULL)", name="ck_verification_review_pair"
        ),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", name="verification_applications_user_id_fkey", ondelete="RESTRICT"),
        nullable=False,
    )
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "organizations.id",
            name="verification_applications_organization_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    role = Column(enums.professional_role, nullable=False)
    registration_number = Column(Text, nullable=True)
    status = Column(
        enums.verification_status,
        server_default=text("'pending'::verification_status"),
        nullable=False,
    )
    submitted_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    reviewed_by = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id", name="verification_applications_reviewed_by_fkey", ondelete="RESTRICT"
        ),
        nullable=True,
    )
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    review_reason = Column(Text, nullable=True)


class VerificationDecision(Base):
    __tablename__ = "verification_decisions"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="verification_decisions_pkey"),
        Index("ix_verification_decisions_history", "application_id", "decided_at"),
        CheckConstraint(
            "decision = ANY (ARRAY['approved'::text, 'rejected'::text, "
            "'more_info_requested'::text, 'suspended'::text])",
            name="ck_verification_decision",
        ),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    application_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "verification_applications.id",
            name="verification_decisions_application_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    reviewer_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id", name="verification_decisions_reviewer_user_id_fkey", ondelete="RESTRICT"
        ),
        nullable=False,
    )
    decision = Column(Text, nullable=False)
    reason = Column(Text, nullable=False)
    decided_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
