from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from src.shared.domain.exceptions import DomainError
from src.shared.domain.ports.unit_of_work import AbstractUnitOfWork
from src.vehicles.application.commands.manage_vehicles import (
    DeleteVehicleCommand,
    DeleteVehicleCommandHandler,
    UpdateVehicleCommand,
    UpdateVehicleCommandHandler,
)
from src.vehicles.domain.entities.vehicle import Vehicle
from src.vehicles.domain.ports.vehicle_repository import VehicleRepository
from src.vehicles.domain.value_objects.catalog_type import CatalogType
from src.vehicles.domain.value_objects.energy_type import EnergyType
from src.vehicles.domain.value_objects.mileage import Mileage
from src.vehicles.domain.value_objects.price import Price


def create_vehicle() -> Vehicle:
    return Vehicle.create(
        brand="Peugeot",
        model="208",
        year=2023,
        price=Price(18000),
        mileage=Mileage(12000),
        energy_type=EnergyType.ESSENCE,
        catalog_type=CatalogType.SALE,
    )


def create_uow() -> AsyncMock:
    unit_of_work = AsyncMock(spec=AbstractUnitOfWork)
    unit_of_work.__aenter__ = AsyncMock(return_value=unit_of_work)
    unit_of_work.__aexit__ = AsyncMock(return_value=None)
    unit_of_work.commit = AsyncMock()
    return unit_of_work


@pytest.mark.asyncio
async def test_update_vehicle_persists_validated_attributes() -> None:
    vehicle = create_vehicle()
    repository = AsyncMock(spec=VehicleRepository)
    repository.find_by_id_for_update.return_value = vehicle
    repository.list_service_catalog.return_value = []
    unit_of_work = create_uow()
    handler = UpdateVehicleCommandHandler(repository, unit_of_work)

    updated = await handler.handle(
        UpdateVehicleCommand(
            vehicle_id=vehicle.id,
            brand="Renault",
            model="Clio",
            year=2024,
            mileage=5000,
            energy_type=EnergyType.HYBRIDE,
            catalog_type=CatalogType.RENTAL,
            monthly_rent=Decimal("299.00"),
        )
    )

    assert updated.brand == "Renault"
    assert updated.catalog_type == CatalogType.RENTAL
    assert updated.monthly_rent == Price(299)
    repository.save.assert_awaited_once_with(updated)
    unit_of_work.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_vehicle_rejects_missing_vehicle() -> None:
    repository = AsyncMock(spec=VehicleRepository)
    repository.find_by_id_for_update.return_value = None
    unit_of_work = create_uow()
    handler = UpdateVehicleCommandHandler(repository, unit_of_work)

    with pytest.raises(DomainError, match="introuvable"):
        await handler.handle(
            UpdateVehicleCommand(
                vehicle_id=create_vehicle().id,
                brand="Renault",
                model="Clio",
                year=2024,
                mileage=5000,
                energy_type=EnergyType.ESSENCE,
                catalog_type=CatalogType.SALE,
                price=Decimal("15000"),
            )
        )

    repository.save.assert_not_awaited()
    unit_of_work.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_vehicle_commits_successful_removal() -> None:
    repository = AsyncMock(spec=VehicleRepository)
    repository.delete_by_id.return_value = True
    unit_of_work = create_uow()
    handler = DeleteVehicleCommandHandler(repository, unit_of_work)
    vehicle_id = create_vehicle().id

    await handler.handle(DeleteVehicleCommand(vehicle_id))

    repository.delete_by_id.assert_awaited_once_with(vehicle_id)
    unit_of_work.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_vehicle_rejects_missing_vehicle() -> None:
    repository = AsyncMock(spec=VehicleRepository)
    repository.delete_by_id.return_value = False
    unit_of_work = create_uow()
    handler = DeleteVehicleCommandHandler(repository, unit_of_work)

    with pytest.raises(DomainError, match="introuvable"):
        await handler.handle(DeleteVehicleCommand(create_vehicle().id))

    unit_of_work.commit.assert_not_awaited()
