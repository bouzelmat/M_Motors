"""Tests unitaires pour le Command Handler AddVehicleCommandHandler."""

from decimal import Decimal
from unittest.mock import AsyncMock
import pytest

from src.shared.domain.exceptions import DomainError
from src.shared.domain.ports.event_bus import AbstractEventBus
from src.shared.domain.ports.unit_of_work import AbstractUnitOfWork
from src.vehicles.application.commands.add_vehicle import (
    AddVehicleCommand,
    AddVehicleCommandHandler,
)
from src.vehicles.domain.events.vehicle_added import VehicleAdded
from src.vehicles.domain.ports.vehicle_repository import VehicleRepository
from src.vehicles.domain.value_objects.catalog_type import CatalogType
from src.vehicles.domain.value_objects.energy_type import EnergyType


@pytest.fixture
def mock_repository() -> AsyncMock:
    repo = AsyncMock(spec=VehicleRepository)
    repo.save = AsyncMock()
    return repo


@pytest.fixture
def mock_uow() -> AsyncMock:
    uow = AsyncMock(spec=AbstractUnitOfWork)
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow.commit = AsyncMock()
    return uow


@pytest.fixture
def mock_event_bus() -> AsyncMock:
    bus = AsyncMock(spec=AbstractEventBus)
    bus.publish = AsyncMock()
    return bus


@pytest.mark.asyncio
async def test_add_vehicle_success(
    mock_repository: AsyncMock,
    mock_uow: AsyncMock,
    mock_event_bus: AsyncMock,
) -> None:
    """Given une commande valide, When handle est exécuté, Then le véhicule est sauvegardé, l'événement est publié et commit est appelé."""
    handler = AddVehicleCommandHandler(
        repository=mock_repository,
        uow=mock_uow,
        event_bus=mock_event_bus,
    )

    command = AddVehicleCommand(
        brand="Peugeot",
        model="208",
        year=2024,
        mileage=10000,
        energy_type=EnergyType.ESSENCE,
        catalog_type=CatalogType.SALE,
        price=Decimal("18000.00"),
    )

    vehicle = await handler.handle(command)

    # Vérification que repository.save a bien été appelé avec l'instance créée
    mock_repository.save.assert_called_once_with(vehicle)

    # Vérification que l'événement de domaine a été publié
    mock_event_bus.publish.assert_called_once()
    published_event = mock_event_bus.publish.call_args[0][0]
    assert isinstance(published_event, VehicleAdded)
    assert published_event.vehicle_id == vehicle.id

    # Vérification que unit_of_work.commit a été exécuté
    mock_uow.commit.assert_called_once()


@pytest.mark.asyncio
async def test_add_vehicle_domain_error_raised(
    mock_repository: AsyncMock,
    mock_uow: AsyncMock,
    mock_event_bus: AsyncMock,
) -> None:
    """Given une commande invalide (prix manquant pour un type SALE), When handle est exécuté, Then une DomainError est levée sans effets de bord."""
    handler = AddVehicleCommandHandler(
        repository=mock_repository,
        uow=mock_uow,
        event_bus=mock_event_bus,
    )

    command = AddVehicleCommand(
        brand="Renault",
        model="Clio",
        year=2023,
        mileage=5000,
        energy_type=EnergyType.DIESEL,
        catalog_type=CatalogType.SALE,
        price=None,  # Invalide pour une vente
    )

    with pytest.raises(DomainError):
        await handler.handle(command)

    # Aucune interaction de persistance, de publication ou de commit ne doit avoir eu lieu
    mock_repository.save.assert_not_called()
    mock_event_bus.publish.assert_not_called()
    mock_uow.commit.assert_not_called()
