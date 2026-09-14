import uuid
import pytest
import pytest_asyncio
from fastapi import FastAPI, Depends, status
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.domain.entities import User
from src.auth.domain.value_objects import Email, Role
from src.auth.infrastructure.orm.user_model import UserModel
from src.auth.infrastructure.security.jwt_service import JWTService
from src.api.dependencies import require_role
from src.shared.infrastructure.database import get_session


@pytest.fixture
def app_test(db_session: AsyncSession) -> FastAPI:
    """Fixture instanciant l'application éphémère de test avec injection de la session de test."""
    app = FastAPI()

    # Surcharge de la dépendance de session pour utiliser la transaction de test
    async def _override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = _override_get_session

    @app.get("/admin-only")
    async def protected_route(user: User = Depends(require_role(Role.ADMIN))):
        return {"message": f"Welcome Admin {user.first_name}"}

    return app


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


@pytest.mark.asyncio
async def test_require_role_admin_success(
    app_test: FastAPI,
    admin_user: User,
    jwt_service: JWTService,
) -> None:
    """Given un utilisateur avec le rôle ADMIN, When il accède à une route protégée, Then l'accès est autorisé."""
    token = jwt_service.create_access_token(
        data={"sub": str(admin_user.id), "email": admin_user.email.value}
    )

    async with AsyncClient(
        transport=ASGITransport(app=app_test),
        base_url="http://test",
        headers={"Authorization": f"Bearer {token}"},
    ) as client:
        response = await client.get("/admin-only")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == f"Welcome Admin {admin_user.first_name}"


@pytest.mark.asyncio
async def test_require_role_client_forbidden(
    app_test: FastAPI,
    client_user: User,
    jwt_service: JWTService,
) -> None:
    """Given un utilisateur avec le rôle CLIENT, When il accède à une route protégée, Then une erreur 403 est renvoyée."""
    token = jwt_service.create_access_token(
        data={"sub": str(client_user.id), "email": client_user.email.value}
    )

    async with AsyncClient(
        transport=ASGITransport(app=app_test),
        base_url="http://test",
        headers={"Authorization": f"Bearer {token}"},
    ) as client:
        response = await client.get("/admin-only")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Insufficient permissions"


@pytest.mark.asyncio
async def test_require_role_invalid_token(app_test: FastAPI) -> None:
    """Token invalide → 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app_test),
        base_url="http://test",
        headers={"Authorization": "Bearer token_invalide_et_incorrect"},
    ) as client:
        response = await client.get("/admin-only")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_require_role_missing_token(app_test: FastAPI) -> None:
    """Pas de token → 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app_test),
        base_url="http://test",
    ) as client:
        response = await client.get("/admin-only")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
