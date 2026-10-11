"""Tests d'intégration pour l'endpoint de téléversement de photos."""

import uuid

import boto3
import pytest
from fastapi import status
from httpx import AsyncClient
from moto import mock_aws

from src.shared.infrastructure.database import get_session
from src.api.main import app
from src.auth.domain.entities import User
from src.auth.domain.value_objects import Email, Role
from src.auth.infrastructure.orm.user_model import UserModel
from src.auth.infrastructure.security.jwt_service import JWTService
from src.config import get_settings
from src.vehicles.application.use_cases.generate_presigned_url import (
    MAX_FILE_SIZE_BYTES,
)
from src.vehicles.domain.entities.vehicle import Vehicle
from src.vehicles.domain.value_objects.catalog_type import CatalogType
from src.vehicles.domain.value_objects.energy_type import EnergyType
from src.vehicles.domain.value_objects.mileage import Mileage
from src.vehicles.domain.value_objects.price import Price
from src.vehicles.infrastructure.repositories.sqlalchemy_vehicle_repository import (
    SQLAlchemyVehicleRepository,
)

AWS_REGION = "eu-west-3"
S3_BUCKET = "m-motors-photos-test"

VALID_PHOTO_PAYLOAD = {
    "file_name": "car.jpg",
    "file_size": 1024,
    "content_type": "image/jpeg",
}


@pytest.fixture(autouse=True)
def override_get_db(db_session):
    """
    Assure que l'AsyncClient utilise la même session de base de données
    que celle où les fixtures (admin_user, existing_vehicle) ont inséré les données.
    Sans cela, l'application ne trouve pas l'utilisateur et retourne 401 Unauthorized.
    """

    async def _get_db():
        yield db_session

    app.dependency_overrides[get_session] = _get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def jwt_service(s3_setup) -> JWTService:
    """
    Fixture fournissant le service JWT pour générer des jetons de test.
    Dépend de s3_setup pour garantir que get_settings() est appelé APRÈS
    que le monkeypatch a configuré les variables d'environnement de test.
    """
    get_settings.cache_clear()
    return JWTService()


@pytest.fixture
def s3_setup(monkeypatch):
    """Fixture initialisant l'environnement S3 simulé via Moto."""
    monkeypatch.setenv("s3_bucket_name", S3_BUCKET)
    monkeypatch.setenv("aws_access_key_id", "testing")
    monkeypatch.setenv("aws_secret_access_key", "testing")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("aws_region", AWS_REGION)
    monkeypatch.setenv("AWS_DEFAULT_REGION", AWS_REGION)
    monkeypatch.setenv("aws_endpoint_url", "")
    monkeypatch.setenv("AWS_ENDPOINT_URL", "")
    monkeypatch.setenv("S3_ENDPOINT_URL", "")
    monkeypatch.setenv("aws_public_endpoint_url", "")
    monkeypatch.setenv("AWS_PUBLIC_ENDPOINT_URL", "")

    get_settings.cache_clear()

    with mock_aws():
        s3 = boto3.client("s3", region_name=AWS_REGION)
        bucket_name = get_settings().s3_bucket_name
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": AWS_REGION},
        )
        yield s3
        get_settings.cache_clear()


@pytest.fixture
async def admin_user(db_session) -> User:
    """Fixture créant et persistant un utilisateur administrateur via le modèle ORM."""
    user = User(
        id=uuid.uuid4(),
        email=Email("admin@m-motors.com"),
        hashed_password="$2b$12$eImiTXuWVxfM37uY4JANjOL.88KV70.4.qXwS1O2J3K4L5M6N7O8P",
        first_name="Admin",
        last_name="System",
        role=Role.ADMIN,
    )
    user_model = UserModel(
        id=str(user.id),
        email=user.email.value,
        hashed_password=user.hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role.value if hasattr(user.role, "value") else user.role,
        is_active=getattr(user, "is_active", True),
        created_at=getattr(user, "created_at", None),
    )
    db_session.add(user_model)
    await db_session.flush()
    await db_session.commit()
    await db_session.refresh(user_model)
    return user


@pytest.fixture
async def client_user(db_session) -> User:
    """Fixture créant un utilisateur CLIENT pour les tests RBAC."""
    user = User(
        id=uuid.uuid4(),
        email=Email("client@m-motors.com"),
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
        is_active=getattr(user, "is_active", True),
        created_at=getattr(user, "created_at", None),
    )
    db_session.add(user_model)
    await db_session.flush()
    await db_session.commit()
    await db_session.refresh(user_model)
    return user


@pytest.fixture
async def existing_vehicle(db_session) -> Vehicle:
    """Fixture créant un véhicule de test valide via la fabrique de domaine Vehicle.create."""
    repo = SQLAlchemyVehicleRepository(db_session)
    vehicle = Vehicle.create(
        brand="BMW",
        model="M3",
        year=2023,
        price=Price(85000.00),
        mileage=Mileage(15000),
        energy_type=EnergyType.ESSENCE,
        catalog_type=CatalogType.SALE,
    )
    await repo.save(vehicle)
    await db_session.commit()
    return vehicle


def get_auth_headers(jwt_service: JWTService, user: User) -> dict[str, str]:
    """Helper pour générer un header Authorization Bearer conforme à l'application."""
    token = jwt_service.create_access_token(
        data={"sub": str(user.id), "email": user.email.value}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_generate_presigned_url_returns_valid_payload(
    async_client: AsyncClient,
    admin_user: User,
    jwt_service: JWTService,
    existing_vehicle: Vehicle,
    s3_setup,
    db_session,
) -> None:
    """Vérifie que l'API retourne une URL pré-signée POST et ses champs signés."""
    headers = get_auth_headers(jwt_service, admin_user)

    response = await async_client.post(
        f"/api/v1/vehicles/{existing_vehicle.id}/photos/presigned-url",
        json=VALID_PHOTO_PAYLOAD,
        headers=headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "url" in data
    assert "fields" in data
    assert data["fields"]["Content-Type"] == "image/jpeg"
    assert data["fields"]["key"].startswith(f"vehicles/{existing_vehicle.id}/")
    assert data["fields"]["key"].endswith(".jpg")
    assert "policy" in data["fields"]
    assert "x-amz-signature" in data["fields"]


@pytest.mark.asyncio
async def test_generate_presigned_post_non_existing_vehicle_returns_404(
    async_client: AsyncClient,
    admin_user: User,
    jwt_service: JWTService,
    s3_setup,
) -> None:
    """Un ID de véhicule inexistant doit retourner 404 Not Found."""
    headers = get_auth_headers(jwt_service, admin_user)
    unknown_id = uuid.uuid4()

    response = await async_client.post(
        f"/api/v1/vehicles/{unknown_id}/photos/presigned-url",
        json=VALID_PHOTO_PAYLOAD,
        headers=headers,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_generate_presigned_post_invalid_mime_returns_400(
    async_client: AsyncClient,
    admin_user: User,
    jwt_service: JWTService,
    existing_vehicle: Vehicle,
) -> None:
    """Un format non autorisé (ex: PDF) doit retourner 400 Bad Request."""
    headers = get_auth_headers(jwt_service, admin_user)

    response = await async_client.post(
        f"/api/v1/vehicles/{existing_vehicle.id}/photos/presigned-url",
        json={
            "file_name": "document.pdf",
            "file_size": 1024,
            "content_type": "application/pdf",
        },
        headers=headers,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_generate_presigned_post_unauthenticated_returns_401(
    async_client: AsyncClient,
    existing_vehicle: Vehicle,
) -> None:
    """Une requête sans token doit retourner 401 Unauthorized."""
    response = await async_client.post(
        f"/api/v1/vehicles/{existing_vehicle.id}/photos/presigned-url",
        json=VALID_PHOTO_PAYLOAD,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_generate_presigned_post_as_client_returns_403(
    async_client: AsyncClient,
    client_user: User,
    jwt_service: JWTService,
    existing_vehicle: Vehicle,
    s3_setup,
) -> None:
    """Un utilisateur CLIENT ne doit pas pouvoir générer une URL pré-signée."""
    headers = get_auth_headers(jwt_service, client_user)

    response = await async_client.post(
        f"/api/v1/vehicles/{existing_vehicle.id}/photos/presigned-url",
        json=VALID_PHOTO_PAYLOAD,
        headers=headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_generate_presigned_post_file_too_large_returns_413(
    async_client: AsyncClient,
    admin_user: User,
    jwt_service: JWTService,
    existing_vehicle: Vehicle,
    s3_setup,
) -> None:
    """Une taille déclarée au-delà de 10 Mo doit retourner 413 Payload Too Large."""
    headers = get_auth_headers(jwt_service, admin_user)

    response = await async_client.post(
        f"/api/v1/vehicles/{existing_vehicle.id}/photos/presigned-url",
        json={
            "file_name": "large.jpg",
            "file_size": MAX_FILE_SIZE_BYTES + 1,
            "content_type": "image/jpeg",
        },
        headers=headers,
    )

    assert response.status_code == status.HTTP_413_CONTENT_TOO_LARGE
