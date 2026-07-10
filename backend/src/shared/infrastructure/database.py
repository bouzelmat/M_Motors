"""Database engine helpers for shared infrastructure concerns."""

from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config import get_settings


@lru_cache(maxsize=1)
def get_engine() -> AsyncEngine:
    """Create the SQLAlchemy async engine used by shared infrastructure."""

    settings = get_settings()
    return create_async_engine(settings.database_url, pool_pre_ping=True)


@lru_cache(maxsize=1)
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Build the async session factory bound to the shared engine."""

    return async_sessionmaker(
        bind=get_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_session() -> AsyncIterator[AsyncSession]:
    """Yield an async database session for request-scoped work."""

    session_factory = get_session_factory()
    async with session_factory() as session:
        yield session


async def execute_health_check(session: AsyncSession) -> None:
    """Execute the minimal query used by the liveness health check."""

    await session.execute(text("SELECT 1"))
