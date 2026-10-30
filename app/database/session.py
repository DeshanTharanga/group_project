"""Async SQLAlchemy sessions. Schema changes run through Alembic, never API startup."""

from collections.abc import AsyncIterator

from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings


def database_url():
    return settings.database_url or URL.create(
        "postgresql+asyncpg",
        username=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
    )


engine = create_async_engine(
    database_url(),
    pool_pre_ping=True,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
)
async_session = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        try:
            yield session
        finally:
            # Remove only files created by an uncommitted/failed request.
            import asyncio

            for path in session.info.pop("new_files", []):
                await asyncio.to_thread(path.unlink, missing_ok=True)


async def close_db():
    await engine.dispose()


async def check_database_connection():
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))
