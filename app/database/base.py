from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class inherited by all SQLAlchemy ORM models."""

    # Fetch database-generated defaults during flush, including UPDATE timestamps.
    __mapper_args__ = {"eager_defaults": True}
