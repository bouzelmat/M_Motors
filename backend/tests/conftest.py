"""Fixtures partagées pour les tests d'intégration."""

from collections.abc import AsyncIterator
from importlib import import_module

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

import src.shared.infrastructure.event_bus as event_bus_module
from src.api.dependencies import get_db_session
from src.shared.infrastructure.database import Base, get_session
from src.shared.infrastructure.messaging.in_memory_event_bus import get_event_bus

# Import ORM models early so they register with Base.metadata before the
# application (and any subscribers) are imported.
for _mod in (
    "src.auth.infrastructure.orm.user_model",
    "src.vehicles.infrastructure.orm.ServiceModel",
    "src.vehicles.infrastructure.orm.VehicleModel",
):
    try:
        import_module(_mod)
    except Exception:
        pass

# Clear any event bus handlers created at import time (avoid side-effects).
class _NoopEventBus:
    def subscribe(self, *a, **kw):
        return None

    async def publish(self, *a, **kw):
        return None

    def clear_handlers(self, *a, **kw):
        return None

# Replace any global event bus with a noop instance to avoid side-effects
try:
    event_bus_module._event_bus = _NoopEventBus()
except Exception:
    try:
        get_event_bus().clear_handlers()
    except Exception:
        pass

from src.api.main import app

TEST_DATABASE_URL = (
    "postgresql+asyncpg://m_motors:m_motors@localhost:5432/test_m_motors"
)

engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_database() -> AsyncIterator[None]:
    """Crée le schéma de test au démarrage et le supprime à la fin."""
    # Ensure all ORM models are imported so they register on Base.metadata
    # Import paths are explicit to avoid lazy-import ordering issues.
    model_modules = [
        "src.auth.infrastructure.orm.user_model",
        "src.vehicles.infrastructure.orm.ServiceModel",
        "src.vehicles.infrastructure.orm.VehicleModel",
    ]
    for mod in model_modules:
        try:
            import_module(mod)
        except Exception:
            # Import errors here should not block test setup; they will surface
            # during tests if a module truly is missing.
            pass

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncIterator[AsyncSession]:
    """Fournit une session isolée dans une transaction rollback."""
    async with engine.connect() as connection:
        transaction = await connection.begin()

        async with TestingSessionLocal(bind=connection) as session:
            await session.execute(text("SET TIME ZONE 'UTC';"))
            nested = await session.begin_nested()

            yield session

            if nested.is_active:
                await nested.rollback()

        await transaction.rollback()


@pytest_asyncio.fixture(scope="function")
async def async_client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    """Client HTTP réutilisable avec surcharge de la session SQLAlchemy."""

    async def override_get_session() -> AsyncIterator[AsyncSession]:
        yield db_session

    # Override route dependencies that yield DB sessions so all route code
    # (auth and vehicles) uses the test session/engine instead of the real one.
    app.dependency_overrides[get_db_session] = override_get_session
    app.dependency_overrides[get_session] = override_get_session

    # Ensure EventBus has no test-unfriendly handlers registered (emails, external)
    try:
        get_event_bus().clear_handlers()
    except Exception:
        pass

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()