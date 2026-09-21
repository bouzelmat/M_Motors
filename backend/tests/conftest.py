"""Fixtures partagées pour les tests d'intégration."""

import os
from collections.abc import AsyncIterator
from importlib import import_module
from uuid import uuid4

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

from src.auth.domain.entities.user import User
from src.auth.domain.value_objects import Email, Role
from src.auth.infrastructure.orm.user_model import UserModel
from src.auth.infrastructure.security.jwt_service import JWTService
from src.vehicles.domain.value_objects.catalog_type import CatalogType
from src.vehicles.domain.value_objects.energy_type import EnergyType
from src.vehicles.domain.value_objects.vehicle_status import VehicleStatus
from src.vehicles.infrastructure.orm.vehicle_model import VehicleModel


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
    "src.vehicles.infrastructure.orm.service_model",
    "src.vehicles.infrastructure.orm.vehicle_model",
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
        "src.vehicles.infrastructure.orm.service_model",
        "src.vehicles.infrastructure.orm.vehicle_model",
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


async def _create_test_user(
    db_session: AsyncSession,
    role: Role,
    email: str,
) -> User:
    user = User(
        id=uuid4(),
        email=Email(email),
        hashed_password="hashed_password_sample",
        first_name=role.value.title(),
        last_name="Test",
        role=role,
    )
    db_session.add(
        UserModel(
            id=str(user.id),
            email=user.email.value,
            hashed_password=user.hashed_password,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at,
        )
    )
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    return await _create_test_user(db_session, Role.CLIENT, "test-user@example.com")


@pytest_asyncio.fixture
async def other_user(db_session: AsyncSession) -> User:
    return await _create_test_user(db_session, Role.CLIENT, "other-user@example.com")


@pytest_asyncio.fixture
async def test_admin(db_session: AsyncSession) -> User:
    return await _create_test_user(db_session, Role.ADMIN, "test-admin@example.com")


@pytest.fixture
def test_user_token(test_user: User) -> str:
    return JWTService().create_access_token(
        data={"sub": str(test_user.id), "email": test_user.email.value}
    )


@pytest.fixture
def test_admin_token(test_admin: User) -> str:
    return JWTService().create_access_token(
        data={"sub": str(test_admin.id), "email": test_admin.email.value}
    )


@pytest_asyncio.fixture
async def client(async_client: AsyncClient) -> AsyncIterator[AsyncClient]:
    yield async_client


@pytest_asyncio.fixture
async def authenticated_client(
    async_client: AsyncClient,
    test_user_token: str,
) -> AsyncIterator[AsyncClient]:
    async_client.headers.update({"Authorization": f"Bearer {test_user_token}"})
    yield async_client


@pytest_asyncio.fixture
async def existing_available_vehicle_id(db_session: AsyncSession) -> str:
    vehicle_id = uuid4()
    db_session.add(
        VehicleModel(
            id=vehicle_id,
            brand="BMW",
            model="M3",
            year=2023,
            price=85000,
            mileage=15000,
            energy_type=EnergyType.ESSENCE,
            status=VehicleStatus.AVAILABLE,
            catalog_type=CatalogType.SALE,
            monthly_rent=None,
        )
    )
    await db_session.flush()
    return str(vehicle_id)
