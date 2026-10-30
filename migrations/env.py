"""Async Alembic environment with explicit online/offline modes."""

import asyncio

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

from app.database.models import Base
from app.database.session import database_url


def configure(connection=None):
    context.configure(
        connection=connection,
        url=database_url() if connection is None else None,
        target_metadata=Base.metadata,
        compare_type=True,
        literal_binds=connection is None,
    )
    with context.begin_transaction():
        context.run_migrations()


async def online():
    engine = create_async_engine(database_url(), poolclass=NullPool)
    try:
        async with engine.connect() as connection:
            await connection.run_sync(configure)
    finally:
        await engine.dispose()


if context.is_offline_mode():
    configure()
else:
    asyncio.run(online())
