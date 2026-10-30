"""PostgreSQL models mapped from the supplied ER diagram."""

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    PrimaryKeyConstraint,
    SmallInteger,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.database import enums
from app.database.base import Base


class IdempotencyRecord(Base):
    __tablename__ = "api_idempotency_records"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="api_idempotency_records_pkey"),
        UniqueConstraint(
            "actor_type",
            "actor_id",
            "operation_key",
            "target_key",
            "idempotency_key",
            name="uq_idempotency_scoped_key",
        ),
        Index("ix_idempotency_expiry", "expires_at"),
        CheckConstraint("request_digest ~ '^[0-9a-fA-F]{64}$'::text", name="ck_idempotency_digest"),
        CheckConstraint(
            "(response_status >= 200) AND (response_status <= 299)", name="ck_idempotency_status"
        ),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    actor_type = Column(enums.idempotency_actor_type, nullable=False)
    actor_id = Column(UUID(as_uuid=True), nullable=False)
    operation_key = Column(Text, nullable=False)
    target_key = Column(Text, server_default=text("'-'::text"), nullable=False)
    idempotency_key = Column(Text, nullable=False)
    request_digest = Column(Text, nullable=False)
    response_status = Column(SmallInteger, nullable=False)
    response_body = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)


class AuditEvent(Base):
    __tablename__ = "audit_events"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="audit_events_pkey"),
        Index("ix_audit_target_time", "target_type", "target_id", "created_at"),
        Index("ix_audit_actor_time", "actor_user_id", "created_at"),
        Index("ix_audit_request", "request_id"),
        CheckConstraint("num_nonnulls(actor_user_id, actor_client_id) <= 1", name="ck_audit_actor"),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    actor_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", name="audit_events_actor_user_id_fkey", ondelete="RESTRICT"),
        nullable=True,
    )
    actor_client_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "integration_clients.id", name="audit_events_actor_client_id_fkey", ondelete="RESTRICT"
        ),
        nullable=True,
    )
    action = Column(Text, nullable=False)
    target_type = Column(Text, nullable=False)
    target_id = Column(UUID(as_uuid=True), nullable=True)
    outcome = Column(Text, nullable=False)
    request_id = Column(Text, nullable=False)
    event_metadata = Column("metadata", JSONB, server_default=text("'{}'::jsonb"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)


class BackupRun(Base):
    __tablename__ = "backup_runs"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="backup_runs_pkey"),
        Index("ix_backup_runs_status_started", "status", "started_at"),
        CheckConstraint(
            "restore_check_status = ANY (ARRAY['not_run'::text, 'passed'::text, 'failed'::text])",
            name="ck_backup_restore_check",
        ),
        CheckConstraint(
            "status = ANY (ARRAY['running'::text, 'succeeded'::text, 'failed'::text])",
            name="ck_backup_status",
        ),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    status = Column(Text, nullable=False)
    database_included = Column(Boolean, server_default=text("false"), nullable=False)
    files_included = Column(Boolean, server_default=text("false"), nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    restore_check_status = Column(Text, server_default=text("'not_run'::text"), nullable=False)
    restore_checked_at = Column(DateTime(timezone=True), nullable=True)
    error_code = Column(Text, nullable=True)


class JobRun(Base):
    __tablename__ = "job_runs"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="job_runs_pkey"),
        UniqueConstraint("job_key", name="job_runs_job_key_key"),
        Index("ix_job_runs_status_created", "status", "created_at"),
        CheckConstraint("attempt_count >= 0", name="ck_job_attempts"),
        CheckConstraint(
            "status = ANY (ARRAY['queued'::text, 'running'::text, "
            "'succeeded'::text, 'failed'::text, 'cancelled'::text])",
            name="ck_job_run_status",
        ),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    job_key = Column(Text, nullable=False)
    job_type = Column(Text, nullable=False)
    status = Column(Text, nullable=False)
    attempt_count = Column(Integer, server_default=text("0"), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    last_error_code = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
