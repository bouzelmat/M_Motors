from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.vehicles.domain.entities.Vehicle import Vehicle
from src.vehicles.domain.value_objects.CatalogType import CatalogType
from src.vehicles.domain.value_objects.EnergyType import EnergyType
from src.vehicles.domain.value_objects.Mileage import Mileage
from src.vehicles.domain.value_objects.Price import Price
from src.vehicles.domain.value_objects.VehicleStatus import VehicleStatus
from src.vehicles.infrastructure.repositories.SQLAlchemyVehicleRepository import (
    SQLAlchemyVehicleRepository,
)


@pytest.mark.asyncio
async def test_list_vehicles_rental_returns_available_vehicles(
    async_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Vérifie que le catalogue LLD ne retourne que les véhicules disponibles."""

    repo = SQLAlchemyVehicleRepository(db_session)

    vehicle_1 = Vehicle(
        id=uuid4(),
        brand="Peugeot",
        model="208",
        year=2023,
        price=Price(20000.0),
        mileage=Mileage(10000),
        energy_type=EnergyType.ESSENCE,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.RENTAL,
        monthly_rent=Price(350.0),
    )

    vehicle_2 = Vehicle(
        id=uuid4(),
        brand="Renault",
        model="Clio",
        year=2022,
        price=Price(18000.0),
        mileage=Mileage(15000),
        energy_type=EnergyType.DIESEL,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.RENTAL,
        monthly_rent=Price(400.0),
    )

    vehicle_3 = Vehicle(
        id=uuid4(),
        brand="Tesla",
        model="Model 3",
        year=2023,
        price=Price(45000.0),
        mileage=Mileage(5000),
        energy_type=EnergyType.ELECTRIQUE,
        status=VehicleStatus.RENTED,
        catalog_type=CatalogType.RENTAL,
        monthly_rent=Price(600.0),
    )

    for vehicle in (vehicle_1, vehicle_2, vehicle_3):
        await repo.save(vehicle)

    await db_session.commit()

    response = await async_client.get(
        "/api/v1/vehicles?mode=rental",
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")

    data = response.json()

    assert len(data) == 2

    for item in data:
        assert "id" in item
        assert "brand" in item
        assert "model" in item
        assert "year" in item
        assert "monthly_rent" in item
        assert "photo_url" in item
        assert "included_services" in item


@pytest.mark.asyncio
async def test_list_vehicles_rental_filter_by_max_monthly_rent(
    async_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Vérifie le filtrage des véhicules par loyer mensuel maximal."""

    repo = SQLAlchemyVehicleRepository(db_session)

    vehicle_1 = Vehicle(
        id=uuid4(),
        brand="A",
        model="A1",
        year=2023,
        price=Price(10000.0),
        mileage=Mileage(20000),
        energy_type=EnergyType.ESSENCE,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.RENTAL,
        monthly_rent=Price(300.0),
    )

    vehicle_2 = Vehicle(
        id=uuid4(),
        brand="B",
        model="B1",
        year=2023,
        price=Price(15000.0),
        mileage=Mileage(10000),
        energy_type=EnergyType.DIESEL,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.RENTAL,
        monthly_rent=Price(450.0),
    )

    for vehicle in (vehicle_1, vehicle_2):
        await repo.save(vehicle)

    await db_session.commit()

    response = await async_client.get(
        "/api/v1/vehicles?mode=rental&max_monthly_rent=400",
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")

    data = response.json()

    assert len(data) == 1
    assert data[0]["monthly_rent"] == "300.00"


@pytest.mark.asyncio
async def test_list_vehicles_sale_mode_returns_empty_for_now(
    async_client: AsyncClient,
) -> None:
    """Vérifie que le mode 'sale' retourne une liste vide tant qu'il n'est pas implémenté."""

    response = await async_client.get(
        "/api/v1/vehicles?mode=sale",
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_vehicle_detail_returns_200_when_available(
    async_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Retourne le détail d'un véhicule disponible."""

    repo = SQLAlchemyVehicleRepository(db_session)

    vehicle = Vehicle(
        id=uuid4(),
        brand="Peugeot",
        model="208",
        year=2023,
        price=Price(20000.0),
        mileage=Mileage(10000),
        energy_type=EnergyType.ESSENCE,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.RENTAL,
        monthly_rent=Price(350.0),
        description="Une voiture compacte",
    )

    await repo.save(vehicle)
    await db_session.commit()

    response = await async_client.get(
        f"/api/v1/vehicles/{vehicle.id}",
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")

    data = response.json()

    assert data["id"] == str(vehicle.id)
    assert data["brand"] == "Peugeot"
    assert data["monthly_rent"] == "350.00"
    assert data["price"] == "20000.00"
    assert data["mileage"] == 10000
    assert data["energy_type"] == "ESSENCE"
    assert data["description"] == "Une voiture compacte"
    assert data["services"] == []


@pytest.mark.asyncio
async def test_get_vehicle_detail_returns_404_when_not_found(
    async_client: AsyncClient,
) -> None:
    """Retourne 404 lorsqu'aucun véhicule ne correspond à l'identifiant demandé."""

    response = await async_client.get(
        f"/api/v1/vehicles/{uuid4()}",
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Véhicule non trouvé",
    }


@pytest.mark.asyncio
async def test_get_vehicle_detail_returns_404_when_vehicle_is_not_available(
    async_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Retourne 404 lorsqu'un véhicule existe mais n'est pas disponible."""

    repo = SQLAlchemyVehicleRepository(db_session)

    vehicle = Vehicle(
        id=uuid4(),
        brand="Tesla",
        model="Model 3",
        year=2023,
        price=Price(45000.0),
        mileage=Mileage(5000),
        energy_type=EnergyType.ELECTRIQUE,
        status=VehicleStatus.RENTED,
        catalog_type=CatalogType.RENTAL,
        monthly_rent=Price(600.0),
    )

    await repo.save(vehicle)
    await db_session.commit()

    response = await async_client.get(
        f"/api/v1/vehicles/{vehicle.id}",
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Véhicule non disponible",
    }
