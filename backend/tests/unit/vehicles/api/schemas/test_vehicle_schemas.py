"""Tests unitaires pour les DTOs Pydantic du contexte Véhicules."""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4
import pytest
from pydantic import ValidationError

from src.vehicles.api.schemas.vehicle_schemas import (
    CreateVehicleRequest,
    VehicleResponse,
)
from src.vehicles.domain.entities.vehicle import Vehicle
from src.vehicles.domain.value_objects.catalog_type import CatalogType
from src.vehicles.domain.value_objects.energy_type import EnergyType
from src.vehicles.domain.value_objects.mileage import Mileage
from src.vehicles.domain.value_objects.price import Price
from src.vehicles.domain.value_objects.vehicle_status import VehicleStatus


def test_create_vehicle_request_valid_sale() -> None:
    """Given des données valides pour la vente, When CreateVehicleRequest est instancié, Then aucune erreur n'est levée."""
    request = CreateVehicleRequest(
        brand="Peugeot",
        model="208",
        year=2024,
        mileage=15000,
        energy_type=EnergyType.ESSENCE,
        catalog_type=CatalogType.SALE,
        price=Decimal("18000.00"),
    )

    assert request.brand == "Peugeot"
    assert request.price == Decimal("18000.00")
    assert request.catalog_type == CatalogType.SALE


def test_create_vehicle_request_valid_rental() -> None:
    """Given des données valides pour la location, When CreateVehicleRequest est instancié, Then aucune erreur n'est levée."""
    request = CreateVehicleRequest(
        brand="Renault",
        model="Clio",
        year=2023,
        mileage=20000,
        energy_type=EnergyType.DIESEL,
        catalog_type=CatalogType.RENTAL,
        monthly_rent=Decimal("250.00"),
    )

    assert request.brand == "Renault"
    assert request.monthly_rent == Decimal("250.00")
    assert request.catalog_type == CatalogType.RENTAL


def test_create_vehicle_request_negative_mileage_raises_validation_error() -> None:
    """Given mileage < 0, When CreateVehicleRequest est instancié, Then une ValidationError est levée."""
    with pytest.raises(ValidationError) as exc_info:
        CreateVehicleRequest(
            brand="Tesla",
            model="Model 3",
            year=2024,
            mileage=-10,
            energy_type=EnergyType.ELECTRIQUE,
            catalog_type=CatalogType.SALE,
            price=Decimal("40000.00"),
        )

    errors = exc_info.value.errors()
    assert any(err["loc"] == ("mileage",) for err in errors)


def test_create_vehicle_request_sale_without_price_raises_validation_error() -> None:
    """Given catalog_type = SALE sans price, When CreateVehicleRequest est instancié, Then une ValidationError est levée."""
    with pytest.raises(ValidationError) as exc_info:
        CreateVehicleRequest(
            brand="BMW",
            model="Série 3",
            year=2022,
            mileage=5000,
            energy_type=EnergyType.DIESEL,
            catalog_type=CatalogType.SALE,
            price=None,
        )

    assert "Un véhicule en vente doit avoir un prix" in str(exc_info.value)


def test_create_vehicle_request_rental_without_monthly_rent_raises_validation_error() -> (
    None
):
    """Given catalog_type = RENTAL sans monthly_rent, When CreateVehicleRequest est instancié, Then une ValidationError est levée."""
    with pytest.raises(ValidationError) as exc_info:
        CreateVehicleRequest(
            brand="Audi",
            model="A3",
            year=2023,
            mileage=12000,
            energy_type=EnergyType.HYBRIDE,
            catalog_type=CatalogType.RENTAL,
            monthly_rent=None,
        )

    assert "Un véhicule en location doit avoir un loyer mensuel" in str(exc_info.value)


def test_vehicle_response_from_domain_entity_with_value_objects() -> None:
    """Given une entité Vehicle avec des Value Objects, When VehicleResponse.model_validate est appelé, Then l'extraction se fait correctement."""
    vehicle = Vehicle(
        id=uuid4(),
        brand="Porsche",
        model="911",
        year=2024,
        price=Price(Decimal("120000.00")),
        mileage=Mileage(1200),
        energy_type=EnergyType.ESSENCE,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.SALE,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    response = VehicleResponse.model_validate(vehicle)

    assert response.id == vehicle.id
    assert response.price == Decimal("120000.00")
    assert response.mileage == 1200
