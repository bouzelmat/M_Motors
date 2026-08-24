from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.vehicles.application.queries.GetRentalCatalogQuery import (
    GetRentalCatalogQuery,
    GetRentalCatalogQueryHandler,
)
from src.vehicles.domain.entities.Vehicle import Vehicle
from src.vehicles.domain.ports.VehicleRepository import VehicleRepository
from src.vehicles.domain.value_objects.CatalogType import CatalogType
from src.vehicles.domain.value_objects.EnergyType import EnergyType
from src.vehicles.domain.value_objects.Mileage import Mileage
from src.vehicles.domain.value_objects.Price import Price
from src.vehicles.domain.value_objects.VehicleSearchCriteria import (
    VehicleSearchCriteria,
)
from src.vehicles.domain.value_objects.VehicleStatus import VehicleStatus


@pytest.mark.asyncio
async def test_handler_uses_repository_with_correct_criteria():
    # Arrange
    mock_repo = AsyncMock(spec=VehicleRepository)
    handler = GetRentalCatalogQueryHandler(mock_repo)
    query = GetRentalCatalogQuery(max_monthly_rent=Decimal("350.00"))

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

    # Act
    result = await handler.handle(query)

    # Assert
    mock_repo.find_by_criteria.assert_called_once()
    called_criteria = mock_repo.find_by_criteria.call_args[0][0]
    assert isinstance(called_criteria, VehicleSearchCriteria)
    assert called_criteria.mode == "rental"
    assert called_criteria.max_monthly_rent == Decimal("350.00")
    assert result == fake_vehicles


@pytest.mark.asyncio
async def test_handler_without_max_rent():
    mock_repo = AsyncMock(spec=VehicleRepository)
    handler = GetRentalCatalogQueryHandler(mock_repo)
    query = GetRentalCatalogQuery()  # max_monthly_rent = None

    await handler.handle(query)

    called_criteria = mock_repo.find_by_criteria.call_args[0][0]
    assert called_criteria.mode == "rental"
    assert called_criteria.max_monthly_rent is None
