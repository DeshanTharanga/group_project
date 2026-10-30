"""PostgreSQL models mapped from the supplied ER diagram."""

from sqlalchemy import (
    BigInteger,
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


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="documents_pkey"),
        UniqueConstraint("storage_key", name="documents_storage_key_key"),
        Index("ix_documents_patient_date", "patient_user_id", "created_at"),
        Index("ix_documents_owner_date", "owner_user_id", "created_at"),
        CheckConstraint(
            "media_type = ANY (ARRAY['application/pdf'::text, "
            "'image/jpeg'::text, 'image/png'::text])",
            name="ck_document_media_type",
        ),
        CheckConstraint(
            "(sha256 IS NULL) OR (sha256 ~ '^[0-9a-fA-F]{64}$'::text)", name="ck_document_sha"
        ),
        CheckConstraint("(byte_size > 0) AND (byte_size <= 10485760)", name="ck_document_size"),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    owner_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", name="documents_owner_user_id_fkey", ondelete="RESTRICT"),
        nullable=False,
    )
    patient_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "patient_profiles.user_id", name="documents_patient_user_id_fkey", ondelete="RESTRICT"
        ),
        nullable=True,
    )
    uploaded_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", name="documents_uploaded_by_fkey", ondelete="RESTRICT"),
        nullable=True,
    )
    source = Column(enums.record_source, nullable=False)
    document_type = Column(Text, nullable=False)
    original_filename = Column(Text, nullable=False)
    storage_key = Column(Text, nullable=False)
    media_type = Column(Text, nullable=False)
    byte_size = Column(BigInteger, nullable=False)
    sha256 = Column(Text, nullable=True)
    status = Column(
        enums.document_status, server_default=text("'active'::document_status"), nullable=False
    )
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    supersedes_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", name="documents_supersedes_id_fkey", ondelete="RESTRICT"),
        nullable=True,
    )


class LabUploadRequest(Base):
    __tablename__ = "lab_upload_requests"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="lab_upload_requests_pkey"),
        UniqueConstraint("request_token_hash", name="lab_upload_requests_request_token_hash_key"),
        Index("ix_lab_requests_lab_status_expiry", "laboratory_id", "status", "expires_at"),
        Index("ix_lab_requests_patient", "patient_user_id", "created_at"),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    patient_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "patient_profiles.user_id",
            name="lab_upload_requests_patient_user_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    laboratory_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "organizations.id", name="lab_upload_requests_laboratory_id_fkey", ondelete="RESTRICT"
        ),
        nullable=False,
    )
    request_token_hash = Column(Text, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(
        enums.upload_request_status,
        server_default=text("'active'::upload_request_status"),
        nullable=False,
    )
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)


class ReportIdentity(Base):
    __tablename__ = "report_identities"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="report_identities_pkey"),
        UniqueConstraint(
            "initial_upload_request_id", name="report_identities_initial_upload_request_id_key"
        ),
        UniqueConstraint("laboratory_id", "lab_reference", name="uq_report_identity_lab_reference"),
        Index("ix_report_identities_patient", "patient_user_id", "created_at"),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    patient_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "patient_profiles.user_id",
            name="report_identities_patient_user_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    laboratory_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "organizations.id", name="report_identities_laboratory_id_fkey", ondelete="RESTRICT"
        ),
        nullable=False,
    )
    lab_reference = Column(Text, nullable=False)
    initial_upload_request_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "lab_upload_requests.id",
            name="report_identities_initial_upload_request_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)


class Report(Base):
    __tablename__ = "reports"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="reports_pkey"),
        Index("ix_reports_patient_date", "patient_user_id", "report_date"),
        Index("ix_reports_lab_date", "laboratory_id", "report_date"),
        Index("ix_reports_identity_date", "report_identity_id", "report_date"),
        CheckConstraint(
            "(supersedes_id IS NULL) = (correction_reason IS NULL)", name="ck_report_correction"
        ),
        UniqueConstraint("supersedes_id", name="uq_reports_replacement"),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    patient_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "patient_profiles.user_id", name="reports_patient_user_id_fkey", ondelete="RESTRICT"
        ),
        nullable=False,
    )
    laboratory_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", name="reports_laboratory_id_fkey", ondelete="RESTRICT"),
        nullable=True,
    )
    report_identity_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "report_identities.id", name="reports_report_identity_id_fkey", ondelete="RESTRICT"
        ),
        nullable=True,
    )
    upload_request_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "lab_upload_requests.id", name="reports_upload_request_id_fkey", ondelete="RESTRICT"
        ),
        nullable=True,
    )
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", name="reports_document_id_fkey", ondelete="RESTRICT"),
        nullable=False,
    )
    report_type = Column(Text, nullable=False)
    report_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    source = Column(enums.record_source, nullable=False)
    uploaded_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", name="reports_uploaded_by_fkey", ondelete="RESTRICT"),
        nullable=True,
    )
    status = Column(
        enums.report_status, server_default=text("'active'::report_status"), nullable=False
    )
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    supersedes_id = Column(
        UUID(as_uuid=True),
        ForeignKey("reports.id", name="reports_supersedes_id_fkey", ondelete="RESTRICT"),
        nullable=True,
    )
    correction_reason = Column(Text, nullable=True)
