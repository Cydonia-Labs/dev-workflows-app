"""Database engine and session management.

Provides an async SQLAlchemy engine and session factory for use
throughout the application. Sessions are created per-request via
the FastAPI dependency system.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import get_settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""


def _make_async_url(url: str) -> str:
    """Convert a postgres:// URL to use the asyncpg driver.

    Args:
        url: PostgreSQL connection string, optionally using the
            postgres:// or postgresql:// scheme.

    Returns:
        Connection string with postgresql+asyncpg:// scheme.
    """
    return url.replace("postgres://", "postgresql+asyncpg://", 1).replace(
        "postgresql://", "postgresql+asyncpg://", 1
    )


settings = get_settings()
engine = create_async_engine(_make_async_url(settings.database_url), echo=False)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session for a single request.

    Yields:
        An async SQLAlchemy session that is closed after the request.
    """
    async with async_session_factory() as session:
        yield session
