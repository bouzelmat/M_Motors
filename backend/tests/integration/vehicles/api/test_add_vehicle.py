"""Tests d'intégration pour l'endpoint POST /api/v1/vehicles."""

import uuid
import pytest
import pytest_asyncio
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.domain.entities import User
from src.auth.domain.value_objects import Email, Role
from src.auth.infrastructure.orm.user_model import UserModel
from src.auth.infrastructure.security.jwt_service import JWTService


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Crée et persiste un utilisateur ADMIN en base de données pour le test."""
    user = User(
        id=uuid.uuid4(),
        email=Email("admin@test.com"),
        hashed_password="hashed_password_sample",
        first_name="Admin",
        last_name="User",
        role=Role.ADMIN,
    )
    user_model = UserModel(
        id=str(user.id),
        email=user.email.value,
        hashed_password=user.hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role.value if hasattr(user.role, "value") else user.role,
        is_active=user.is_active,
        created_at=user.created_at,
    )
    db_session.add(user_model)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def client_user(db_session: AsyncSession) -> User:
    """Crée et persiste un utilisateur CLIENT en base de données pour le test."""
    user = User(
        id=uuid.uuid4(),
        email=Email("client@test.com"),
        hashed_password="hashed_password_sample",
        first_name="Client",
        last_name="User",
        role=Role.CLIENT,
    )
    user_model = UserModel(
        id=str(user.id),
        email=user.email.value,
        hashed_password=user.hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role.value if hasattr(user.role, "value") else user.role,
        is_active=user.is_active,
        created_at=user.created_at,
    )
    db_session.add(user_model)
    await db_session.flush()
    return user


@pytest.fixture
def jwt_service() -> JWTService:
    """Fixture fournissant une instance de JWTService."""
    return JWTService()


def get_auth_headers(jwt_service, user) -> dict[str, str]:
    """Helper pour générer un header Authorization Bearer conforme à l'application."""
    token = jwt_service.create_access_token(
        data={"sub": str(user.id), "email": user.email.value}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_add_vehicle_as_admin_returns_201(
    async_client: AsyncClient,
    admin_user,
    jwt_service,
) -> None:
    """Given ADMIN authentifié, When données valides soumises, Then 201 Created et présent dans le catalogue."""
    headers = get_auth_headers(jwt_service, admin_user)
    payload = {
        "brand": "Peugeot",
        "model": "308",
        "year": 2023,
        "mileage": 15000,
        "energy_type": "DIESEL",
        "catalog_type": "RENTAL",
        "monthly_rent": "450.00",
        "description": "Excellente condition",
    }

    response = await async_client.post(
        "/api/v1/vehicles",
        json=payload,
        headers=headers,
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["brand"] == "Peugeot"
    assert "id" in data

    # Vérification de l'apparition dans le catalogue via l'endpoint GET
    catalog_response = await async_client.get("/api/v1/vehicles?mode=rental")
    assert catalog_response.status_code == status.HTTP_200_OK
    vehicles = catalog_response.json()
    assert any(v["id"] == data["id"] for v in vehicles)


@pytest.mark.asyncio
async def test_add_vehicle_as_client_returns_403(
    async_client: AsyncClient,
    client_user,
    jwt_service,
) -> None:
    """Given rôle CLIENT, When tentative de création, Then 403 Forbidden."""
    headers = get_auth_headers(jwt_service, client_user)
    payload = {
        "brand": "Renault",
        "model": "Clio",
        "year": 2022,
        "price": "12000.00",
        "mileage": 30000,
        "energy_type": "ESSENCE",
        "catalog_type": "SALE",
    }

    response = await async_client.post(
        "/api/v1/vehicles",
        json=payload,
        headers=headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_add_vehicle_unauthenticated_returns_401(
    async_client: AsyncClient,
) -> None:
    """Given requête sans en-tête d'authentification, When POST appelé, Then 401 Unauthorized."""
    payload = {
        "brand": "Renault",
        "model": "Clio",
        "year": 2022,
        "price": "12000.00",
        "mileage": 30000,
        "energy_type": "ESSENCE",
        "catalog_type": "SALE",
    }

    response = await async_client.post("/api/v1/vehicles", json=payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_add_vehicle_invalid_data_returns_422(
    async_client: AsyncClient,
    admin_user,
    jwt_service,
) -> None:
    """Given données invalides (kilométrage négatif), When POST appelé, Then 422 Unprocessable Entity."""
    headers = get_auth_headers(jwt_service, admin_user)
    payload = {
        "brand": "Renault",
        "model": "Clio",
        "year": 2022,
        "price": "12000.00",  # Ajout de la valeur obligatoire du Price VO
        "mileage": -100,  # Valeur invalide testée
        "energy_type": "ESSENCE",
        "catalog_type": "SALE",
    }

    response = await async_client.post(
        "/api/v1/vehicles",
        json=payload,
        headers=headers,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
