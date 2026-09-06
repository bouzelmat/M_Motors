from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.vehicles.application.queries.search_vehicles_query import (
    SearchVehiclesQuery,
    SearchVehiclesQueryHandler,
)
from src.vehicles.domain.entities.vehicle import Vehicle
from src.vehicles.domain.ports.vehicle_repository import VehicleRepository
from src.vehicles.domain.value_objects.catalog_type import CatalogType
from src.vehicles.domain.value_objects.energy_type import EnergyType
from src.vehicles.domain.value_objects.mileage import Mileage
from src.vehicles.domain.value_objects.price import Price
from src.vehicles.domain.value_objects.vehicle_search_criteria import (
    VehicleSearchCriteria,
)
from src.vehicles.domain.value_objects.vehicle_status import VehicleStatus


@pytest.mark.asyncio
async def test_handler_passes_criteria_to_repository():
    """Le handler transmet les critères reçus au repository."""

    mock_repo = AsyncMock(spec=VehicleRepository)
    handler = SearchVehiclesQueryHandler(mock_repo)

    criteria = VehicleSearchCriteria(
        mode="rental",
        max_monthly_rent=Decimal("350.00"),
        brand="Peugeot",
        max_mileage=50000,
        fuel_type="ESSENCE",
    )

    query = SearchVehiclesQuery(criteria=criteria)

    fake_vehicles = [
        Vehicle(
            id=uuid4(),
            brand="Peugeot",
            model="208",
            year=2023,
            price=Price(20000.0),
            mileage=Mileage(10000),
            energy_type=EnergyType.ESSENCE,
            status=VehicleStatus.AVAILABLE,
            catalog_type=CatalogType.RENTAL,
            monthly_rent=Price(300.0),
        )
    ]

    mock_repo.find_by_criteria.return_value = fake_vehicles

    result = await handler.handle(query)

    mock_repo.find_by_criteria.assert_called_once_with(criteria)
    assert result == fake_vehicles


@pytest.mark.asyncio
async def test_handler_supports_sale_criteria():
    """Le handler transmet également les critères du catalogue achat."""

    mock_repo = AsyncMock(spec=VehicleRepository)
    handler = SearchVehiclesQueryHandler(mock_repo)

    criteria = VehicleSearchCriteria(
        mode="sale",
        max_price=Decimal("25000.00"),
        brand="Peugeot",
        max_mileage=60000,
        fuel_type="ESSENCE",
    )

    query = SearchVehiclesQuery(criteria=criteria)

    fake_vehicles = [
        Vehicle(
            id=uuid4(),
            brand="Peugeot",
            model="308",
            year=2022,
            price=Price(22000.0),
            mileage=Mileage(30000),
            energy_type=EnergyType.ESSENCE,
            status=VehicleStatus.AVAILABLE,
            catalog_type=CatalogType.SALE,
        )
    ]

    mock_repo.find_by_criteria.return_value = fake_vehicles

    result = await handler.handle(query)

    mock_repo.find_by_criteria.assert_called_once_with(criteria)
    assert result == fake_vehicles


@pytest.mark.asyncio
async def test_handler_returns_empty_list_when_repository_returns_no_vehicle():
    """Le handler retourne une liste vide si aucun véhicule ne correspond."""

    mock_repo = AsyncMock(spec=VehicleRepository)
    handler = SearchVehiclesQueryHandler(mock_repo)

    criteria = VehicleSearchCriteria(mode="rental")
    query = SearchVehiclesQuery(criteria=criteria)

    mock_repo.find_by_criteria.return_value = []

    result = await handler.handle(query)

    mock_repo.find_by_criteria.assert_called_once_with(criteria)
    assert result == []
