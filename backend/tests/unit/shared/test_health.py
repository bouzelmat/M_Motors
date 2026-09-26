"""Health endpoint tests."""

from collections.abc import AsyncIterator
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

# Remplacement de l'ancienne dépendance API par le point d'entrée de la DB
from src.shared.infrastructure.database import get_session
from src.api.main import app


class DummySession:
    """Minimal async session double for the health route test."""

    def __init__(self) -> None:
        self.execute = AsyncMock(return_value=None)


async def override_get_db_session() -> AsyncIterator[DummySession]:
    """Yield a fake session for the health endpoint test."""

    session = DummySession()
    yield session


def test_health_endpoint_reports_database_reachable() -> None:
    """The health endpoint should confirm a working database connection."""

    # Surcharge de get_session pour intercepter SessionDep proprement
    app.dependency_overrides[get_session] = override_get_db_session

    try:
        client = TestClient(app)
        response = client.get("/health")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "reachable"}
