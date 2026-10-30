"""PostgreSQL models mapped from the supplied ER diagram."""

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    PrimaryKeyConstraint,
    SmallInteger,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID

from app.database import enums
from app.database.base import Base


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="roles_pkey"),
        UniqueConstraint("code", name="roles_code_key"),
        UniqueConstraint("label", name="roles_label_key"),
        CheckConstraint(
            "code = ANY (ARRAY['patient'::text, 'doctor'::text, "
            "'pharmacist'::text, 'lab_staff'::text, 'admin'::text, "
            "'super_admin'::text])",
            name="ck_roles_code",
        ),
    )
    id = Column(SmallInteger, nullable=False)
    code = Column(Text, nullable=False)
    label = Column(Text, nullable=False)


class UserRole(Base):
    __tablename__ = "user_roles"
    __table_args__ = (PrimaryKeyConstraint("user_id", "role_id", name="user_roles_pkey"),)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", name="user_roles_user_id_fkey", ondelete="RESTRICT"),
        nullable=False,
    )
    role_id = Column(
        SmallInteger,
        ForeignKey("roles.id", name="user_roles_role_id_fkey", ondelete="RESTRICT"),
        nullable=False,
    )
    assigned_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", name="user_roles_assigned_by_fkey", ondelete="RESTRICT"),
        nullable=True,
    )
    assigned_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="users_pkey"),
        UniqueConstraint("firebase_uid", name="users_firebase_uid_key"),
        Index("uq_users_email_ci", text("lower(email)"), unique=True),
    )
    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), nullable=False)
    firebase_uid = Column(Text, nullable=False)
    email = Column(Text, nullable=True)
    display_name = Column(Text, nullable=False)
    phone = Column(Text, nullable=True)
    status = Column(
        enums.account_status, server_default=text("'pending'::account_status"), nullable=False
    )
    created_at = Column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=text("now()"),
        onupdate=text("now()"),
        nullable=False,
    )
