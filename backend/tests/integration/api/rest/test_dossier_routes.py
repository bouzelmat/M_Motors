"""Tests d'intégration HTTP pour les routes FastAPI /api/v1/dossiers."""

from uuid import uuid4

import pytest
from httpx import AsyncClient
from starlette import status


@pytest.mark.asyncio
async def test_create_dossier_unauthorized(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/dossiers",
        json={"vehicle_id": str(uuid4())},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_create_dossier_invalid_payload(
    authenticated_client: AsyncClient,
) -> None:
    # Kilométrage négatif invalide
    payload = {
        "vehicle_id": str(uuid4()),
        "trade_in": {
            "registration": "AB-123-CD",
            "mileage": -500,
        },
    }
    response = await authenticated_client.post("/api/v1/dossiers", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_create_dossier_success(
    authenticated_client: AsyncClient,
    existing_available_vehicle_id: str,
) -> None:
    payload = {
        "vehicle_id": existing_available_vehicle_id,
        "trade_in": {
            "registration": "AA-888-ZZ",
            "mileage": 15000,
        },
        "financing_plan": {
            "down_payment": "2000.00",
            "duration_months": 24,
            "monthly_payment": "150.00",
        },
    }

    response = await authenticated_client.post("/api/v1/dossiers", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "id" in data
    assert data["vehicle_id"] == existing_available_vehicle_id
    assert data["status"] == "DRAFT"