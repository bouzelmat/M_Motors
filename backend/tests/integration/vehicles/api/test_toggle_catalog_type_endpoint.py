from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import FastAPI, status, HTTPException
from fastapi.testclient import TestClient

from src.vehicles.api.dependencies import (
    check_toggle_feature_enabled,
    get_current_admin_user,
    get_toggle_vehicle_type_handler,
)
from src.vehicles.api.routes.vehicle_routes import router
from src.vehicles.application.commands.toggle_vehicle_type import (
    ToggleVehicleTypeCommandHandler,
)
from src.vehicles.domain.entities.vehicle import Vehicle
from src.vehicles.domain.value_objects.catalog_type import CatalogType
from src.vehicles.domain.value_objects.energy_type import EnergyType
from src.vehicles.domain.value_objects.mileage import Mileage
from src.vehicles.domain.value_objects.price import Price
from src.vehicles.domain.value_objects.vehicle_status import VehicleStatus

# Application de test isolée
app = FastAPI()
app.include_router(router)


@pytest.fixture
def override_feature_flag():
    """Bypasse le Feature Flag pour exécuter les tests d'intégration."""
    app.dependency_overrides[check_toggle_feature_enabled] = lambda: None
    yield
    app.dependency_overrides.pop(check_toggle_feature_enabled, None)


@pytest.fixture
def override_admin_auth():
    """Simule la présence d'un utilisateur administrateur authentifié."""
    app.dependency_overrides[get_current_admin_user] = lambda: {
        "sub": "admin",
        "role": "admin",
    }
    yield
    app.dependency_overrides.pop(get_current_admin_user, None)


@pytest.fixture
def client(override_feature_flag, override_admin_auth):
    return TestClient(app)


def test_toggle_catalog_type_success_no_active_dossier(client):
    """Scénario : Bascule réussie sans dossier actif -> 200 OK."""
    vehicle_id = uuid4()
    updated_vehicle = Vehicle(
        id=vehicle_id,
        brand="BMW",
        model="i4",
        year=2024,
        price=None,
        mileage=Mileage(15000),
        energy_type=EnergyType.ESSENCE,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.RENTAL,
        monthly_rent=Price(Decimal("750.00")),
    )

    mock_handler = AsyncMock(spec=ToggleVehicleTypeCommandHandler)
    mock_handler.handle.return_value = updated_vehicle

    app.dependency_overrides[get_toggle_vehicle_type_handler] = lambda: mock_handler

    response = client.patch(
        f"/vehicles/{vehicle_id}/catalog-type",
        json={"new_price": 750.00, "confirm": False},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(vehicle_id)
    assert data["catalog_type"] == "RENTAL"
    assert data["monthly_rent"] == "750.00"

    app.dependency_overrides.pop(get_toggle_vehicle_type_handler, None)


def test_toggle_catalog_type_conflict_active_dossier_no_confirm(client):
    """Scénario : Conflit dossier actif sans confirmation -> 409 Conflict."""
    from src.vehicles.application.exceptions import ActiveDossierWarningException

    vehicle_id = uuid4()

    mock_handler = AsyncMock(spec=ToggleVehicleTypeCommandHandler)
    mock_handler.handle.side_effect = ActiveDossierWarningException(
        vehicle_id=vehicle_id
    )

    app.dependency_overrides[get_toggle_vehicle_type_handler] = lambda: mock_handler

    response = client.patch(
        f"/vehicles/{vehicle_id}/catalog-type",
        json={"new_price": 750.00, "confirm": False},
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    data = response.json()
    assert data["vehicle_id"] == str(vehicle_id)
    assert data["requires_confirmation"] is True

    app.dependency_overrides.pop(get_toggle_vehicle_type_handler, None)


def test_toggle_catalog_type_success_active_dossier_with_confirm(client):
    """Scénario : Conflit dossier actif avec confirmation -> 200 OK."""
    vehicle_id = uuid4()
    updated_vehicle = Vehicle(
        id=vehicle_id,
        brand="BMW",
        model="i4",
        year=2024,
        price=None,
        mileage=Mileage(15000),
        energy_type=EnergyType.ESSENCE,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.RENTAL,
        monthly_rent=Price(Decimal("750.00")),
    )

    mock_handler = AsyncMock(spec=ToggleVehicleTypeCommandHandler)
    mock_handler.handle.return_value = updated_vehicle

    app.dependency_overrides[get_toggle_vehicle_type_handler] = lambda: mock_handler

    response = client.patch(
        f"/vehicles/{vehicle_id}/catalog-type",
        json={"new_price": 750.00, "confirm": True},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["catalog_type"] == "RENTAL"

    app.dependency_overrides.pop(get_toggle_vehicle_type_handler, None)


def test_toggle_catalog_type_vehicle_not_found(client):
    """Scénario : Véhicule introuvable -> 404 Not Found."""
    from src.shared.domain.exceptions import NotFoundError

    vehicle_id = uuid4()

    mock_handler = AsyncMock(spec=ToggleVehicleTypeCommandHandler)
    mock_handler.handle.side_effect = NotFoundError(
        f"Véhicule introuvable : {vehicle_id}"
    )

    app.dependency_overrides[get_toggle_vehicle_type_handler] = lambda: mock_handler

    response = client.patch(
        f"/vehicles/{vehicle_id}/catalog-type",
        json={"new_price": 750.00},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "introuvable" in response.json()["detail"]

    app.dependency_overrides.pop(get_toggle_vehicle_type_handler, None)


def test_toggle_catalog_type_invalid_request_body(client):
    """Scénario : Corps de requête invalide (new_price <= 0) -> 422 Unprocessable Entity."""
    vehicle_id = uuid4()

    response = client.patch(
        f"/vehicles/{vehicle_id}/catalog-type",
        json={"new_price": -50.00},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_toggle_catalog_type_unauthorized_non_admin(override_feature_flag):
    """Scénario : Accès non admin refusé -> 403 Forbidden."""

    # Simuler un utilisateur non-admin
    def override_non_admin_user():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs.",
        )

    app.dependency_overrides[get_current_admin_user] = override_non_admin_user
    local_client = TestClient(app)

    vehicle_id = uuid4()
    response = local_client.patch(
        f"/vehicles/{vehicle_id}/catalog-type",
        json={"new_price": 750.00},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    app.dependency_overrides.pop(get_current_admin_user, None)
