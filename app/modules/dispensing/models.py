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
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID

from app.database import enums
from app.database.base import Base


class DispensingEvent(Base):
    __tablename__ = "dispensing_events"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="dispensing_events_pkey"),
        UniqueConstraint("request_key", name="dispensing_events_request_key_key"),
        UniqueConstraint("reversal_of_id", name="uq_dispensing_single_reversal"),
        Index("ix_dispensing_prescription_date", "prescription_id", "dispensed_at"),
        Index("ix_dispensing_pharmacist_date", "pharmacist_user_id", "dispensed_at"),
        CheckConstraint(
            "(reversal_of_id IS NULL) = (reason IS NULL)", name="ck_dispensing_reversal"
        ),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    prescription_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "prescriptions.id", name="dispensing_events_prescription_id_fkey", ondelete="RESTRICT"
        ),
        nullable=False,
    )
    pharmacist_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id", name="dispensing_events_pharmacist_user_id_fkey", ondelete="RESTRICT"
        ),
        nullable=False,
    )
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "organizations.id", name="dispensing_events_organization_id_fkey", ondelete="RESTRICT"
        ),
        nullable=False,
    )
    share_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "prescription_shares.id", name="dispensing_events_share_id_fkey", ondelete="RESTRICT"
        ),
        nullable=True,
    )
    dispensed_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    request_key = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    reversal_of_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "dispensing_events.id",
            name="dispensing_events_reversal_of_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)


class DispensingItem(Base):
    __tablename__ = "dispensing_items"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="dispensing_items_pkey"),
        UniqueConstraint("event_id", "prescription_item_id", name="uq_dispensing_event_item"),
        Index("ix_dispensing_items_item", "prescription_item_id"),
        CheckConstraint("quantity > (0)::numeric", name="ck_dispensing_quantity"),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    event_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "dispensing_events.id", name="dispensing_items_event_id_fkey", ondelete="RESTRICT"
        ),
        nullable=False,
    )
    prescription_item_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "prescription_items.id",
            name="dispensing_items_prescription_item_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    quantity = Column(Numeric(12, 3), nullable=False)
    quantity_unit = Column(Text, nullable=False)


class PrescriptionShare(Base):
    __tablename__ = "prescription_shares"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="prescription_shares_pkey"),
        UniqueConstraint("claim_token_hash", name="prescription_shares_claim_token_hash_key"),
        Index(
            "ix_prescription_shares_expiry",
            "status",
            "claim_expires_at",
            "confirmed_access_expires_at",
        ),
        CheckConstraint("(claimed_by IS NULL) = (claimed_at IS NULL)", name="ck_share_claim_pair"),
        CheckConstraint(
            "(confirmed_at IS NULL) = (confirmed_access_expires_at IS NULL)",
            name="ck_share_access_expiry",
        ),
        CheckConstraint(
            "(status = 'revoked'::share_status) = (revoked_at IS NOT NULL)", name="ck_share_revoked"
        ),
        CheckConstraint(
            "(status <> 'confirmed'::share_status) OR ((confirmed_at IS NOT "
            "NULL) AND (claimed_by IS NOT NULL))",
            name="ck_share_confirm",
        ),
        CheckConstraint(
            "(claimed_by IS NULL) = (claimed_organization_id IS NULL)", name="ck_share_claim_org"
        ),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    prescription_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "prescriptions.id", name="prescription_shares_prescription_id_fkey", ondelete="RESTRICT"
        ),
        nullable=False,
    )
    patient_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "patient_profiles.user_id",
            name="prescription_shares_patient_user_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    claim_token_hash = Column(Text, nullable=False)
    status = Column(
        enums.share_status, server_default=text("'created'::share_status"), nullable=False
    )
    claim_expires_at = Column(DateTime(timezone=True), nullable=False)
    claimed_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", name="prescription_shares_claimed_by_fkey", ondelete="RESTRICT"),
        nullable=True,
    )
    claimed_organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "organizations.id",
            name="prescription_shares_claimed_organization_id_fkey",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    claimed_at = Column(DateTime(timezone=True), nullable=True)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    confirmed_access_expires_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
