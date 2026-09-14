"""Fixtures partagées pour les tests d'intégration."""

import os
from collections.abc import AsyncIterator
from importlib import import_module

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool


@pytest.fixture(scope="session", autouse=True)
def setup_test_env() -> None:
    """Injecte TOUTES les variables d'environnement obligatoires avant les imports de l'application."""
    os.environ.setdefault(
        "DATABASE_URL",
        "postgresql+asyncpg://m_motors:m_motors@localhost:5432/test_m_motors",
    )
    os.environ.setdefault(
        "JWT_SECRET_KEY", "fake_secret_key_for_testing_only_123456789"
    )
    os.environ.setdefault("JWT_ALGORITHM", "HS256")

    os.environ.setdefault("s3_bucket_name", "m-motors-photos-test")
    os.environ.setdefault("aws_access_key_id", "testing")
    os.environ.setdefault("aws_secret_access_key", "testing")
    os.environ.setdefault("aws_region", "eu-west-3")


import src.shared.infrastructure.event_bus as event_bus_module
from src.shared.infrastructure.database import Base, get_session
from src.shared.infrastructure.messaging.in_memory_event_bus import get_event_bus

# Enregistrement précoce des modèles ORM
for _mod in (
    "src.auth.infrastructure.orm.user_model",
    "src.vehicles.infrastructure.orm.ServiceModel",
    "src.vehicles.infrastructure.orm.VehicleModel",
    "src.vehicles.infrastructure.orm.vehicle_photo_model",
):
    try:
        import_module(_mod)
    except Exception:
        pass


class _NoopEventBus:
    def subscribe(self, *a, **kw):
        return None

    async def publish(self, *a, **kw):
        return None

    def clear_handlers(self, *a, **kw):
        return None


try:
    event_bus_module._event_bus = _NoopEventBus()
except Exception:
    try:
        get_event_bus().clear_handlers()
    except Exception:
        pass

from src.api.main import app

TEST_DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://m_motors:m_motors@localhost:5432/test_m_motors",
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
    model_modules = [
        "src.auth.infrastructure.orm.user_model",
        "src.vehicles.infrastructure.orm.ServiceModel",
        "src.vehicles.infrastructure.orm.VehicleModel",
        "src.vehicles.infrastructure.orm.vehicle_photo_model",
    ]
    for mod in model_modules:
        try:
            import_module(mod)
        except Exception:
            pass

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncIterator[AsyncSession]:
    """Fournit une session entièrement isolée via une transaction et un SAVEPOINT imbriqué."""
    async with engine.connect() as connection:
        transaction = await connection.begin()

        async with TestingSessionLocal(bind=connection) as session:
            await session.execute(text("SET TIME ZONE 'UTC';"))
            nested = await session.begin_nested()

            @event.listens_for(session.sync_session, "after_transaction_end")
            def restart_savepoint(sync_session, transaction_arg):
                nonlocal nested
                if transaction_arg.nested and not nested.is_active:
                    nested = session.begin_nested()

            yield session

            if session.is_active:
                await session.close()

        await transaction.rollback()


@pytest_asyncio.fixture(scope="function")
async def async_client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    """Client HTTP réutilisable avec surcharge de la session SQLAlchemy."""

    async def override_get_session() -> AsyncIterator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

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