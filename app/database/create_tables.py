"""Compatibility entry point: run versioned migrations instead of create_all."""

from alembic import command
from alembic.config import Config

if __name__ == "__main__":
    command.upgrade(Config("alembic.ini"), "head")
