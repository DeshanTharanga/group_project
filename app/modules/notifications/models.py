"""PostgreSQL models mapped from the supplied ER diagram."""

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    PrimaryKeyConstraint,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="notifications_pkey"),
        UniqueConstraint("dedupe_key", name="notifications_dedupe_key_key"),
        Index("ix_notifications_user_unread", "user_id", "created_at"),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", name="notifications_user_id_fkey", ondelete="RESTRICT"),
        nullable=False,
    )
    notification_type = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    body = Column(Text, nullable=False)
    related_type = Column(Text, nullable=True)
    related_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    dedupe_key = Column(Text, nullable=False)
