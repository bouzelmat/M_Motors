from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4
import pytest

from src.shared.domain.exceptions import DomainError
from src.shared.domain.ports.event_bus import AbstractEventBus
from src.shared.domain.ports.unit_of_work import AbstractUnitOfWork
from src.vehicles.application.commands.toggle_vehicle_type import (
    ToggleVehicleTypeCommand,
    ToggleVehicleTypeCommandHandler,
)
from src.vehicles.application.exceptions import ActiveDossierWarningException
from src.vehicles.domain.entities.vehicle import Vehicle
from src.vehicles.domain.events.vehicle_listed_for_rental import VehicleListedForRental
from src.vehicles.domain.events.vehicle_listed_for_sale import VehicleListedForSale
from src.vehicles.domain.ports.dossier_existence_port import DossierExistencePort
from src.vehicles.domain.ports.vehicle_repository import VehicleRepository
from src.vehicles.domain.value_objects.catalog_type import CatalogType
from src.vehicles.domain.value_objects.energy_type import EnergyType
from src.vehicles.domain.value_objects.mileage import Mileage
from src.vehicles.domain.value_objects.price import Price
from src.vehicles.domain.value_objects.vehicle_status import VehicleStatus


class FakeVehicleRepository(VehicleRepository):
    def __init__(self, vehicles: list[Vehicle] | None = None) -> None:
        self.vehicles: dict[UUID, Vehicle] = {v.id: v for v in (vehicles or [])}
        self.saved_vehicles: list[Vehicle] = []

    async def get_by_id(self, vehicle_id: UUID) -> Vehicle | None:
        return self.vehicles.get(vehicle_id)

    async def save(self, vehicle: Vehicle) -> None:
        self.vehicles[vehicle.id] = vehicle
        self.saved_vehicles.append(vehicle)


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self) -> None:
        self.committed = False

    async def __aenter__(self) -> "FakeUnitOfWork":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        pass

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        pass


class FakeEventBus(AbstractEventBus):
    def __init__(self) -> None:
        self.published_events: list[Any] = []

    async def publish(self, event: Any) -> None:
        self.published_events.append(event)

    async def subscribe(self, event_type: Any, handler: Any) -> None:
        """Implémentation obligatoire de la méthode abstraite du port."""
        pass


class FakeDossierExistencePort(DossierExistencePort):
    def __init__(self, has_active: bool = False) -> None:
        self.has_active = has_active

    async def has_active_dossier_for_vehicle(self, vehicle_id: UUID) -> bool:
        return self.has_active


def create_test_vehicle(catalog_type: CatalogType) -> Vehicle:
    return Vehicle(
        id=uuid4(),
        brand="Tesla",
        model="Model 3",
        year=2024,
        mileage=Mileage(15000),
        energy_type=EnergyType.ESSENCE,
        status=VehicleStatus.AVAILABLE,
        catalog_type=catalog_type,
        price=Price(Decimal("30000")) if catalog_type == CatalogType.SALE else None,
        monthly_rent=(
            Price(Decimal("500")) if catalog_type == CatalogType.RENTAL else None
        ),
    )


@pytest.mark.asyncio
async def test_toggle_sale_to_rental_success() -> None:
    vehicle = create_test_vehicle(CatalogType.SALE)
    repo = FakeVehicleRepository([vehicle])
    uow = FakeUnitOfWork()
    bus = FakeEventBus()
    dossier_port = FakeDossierExistencePort(has_active=False)
    handler = ToggleVehicleTypeCommandHandler(repo, uow, bus, dossier_port)
    cmd = ToggleVehicleTypeCommand(
        vehicle_id=vehicle.id,
        new_price=Decimal("600.00"),
    )
    result = await handler.handle(cmd)
    assert result.catalog_type == CatalogType.RENTAL
    assert result.monthly_rent == Price(Decimal("600.00"))
    assert result.price is None
    assert uow.committed is True
    assert len(bus.published_events) == 1
    event = bus.published_events[0]
    assert isinstance(event, VehicleListedForRental)
    assert event.vehicle_id == vehicle.id
    assert event.previous_catalog_type == "SALE"
    assert event.new_catalog_type == "RENTAL"
    assert event.new_monthly_rent == Decimal("600.00")


@pytest.mark.asyncio
async def test_toggle_rental_to_sale_success() -> None:
    vehicle = create_test_vehicle(CatalogType.RENTAL)
    repo = FakeVehicleRepository([vehicle])
    uow = FakeUnitOfWork()
    bus = FakeEventBus()
    dossier_port = FakeDossierExistencePort(has_active=False)
    handler = ToggleVehicleTypeCommandHandler(repo, uow, bus, dossier_port)
    cmd = ToggleVehicleTypeCommand(
        vehicle_id=vehicle.id,
        new_price=Decimal("25000.00"),
    )
    result = await handler.handle(cmd)
    assert result.catalog_type == CatalogType.SALE
    assert result.price == Price(Decimal("25000.00"))
    assert result.monthly_rent is None
    assert uow.committed is True
    assert len(bus.published_events) == 1
    event = bus.published_events[0]
    assert isinstance(event, VehicleListedForSale)
    assert event.vehicle_id == vehicle.id
    assert event.previous_catalog_type == "RENTAL"
    assert event.new_catalog_type == "SALE"
    assert event.new_price == Decimal("25000.00")


@pytest.mark.asyncio
async def test_toggle_invalid_price_raises_domain_error() -> None:
    vehicle = create_test_vehicle(CatalogType.SALE)
    repo = FakeVehicleRepository([vehicle])
    uow = FakeUnitOfWork()
    bus = FakeEventBus()
    dossier_port = FakeDossierExistencePort(has_active=False)
    handler = ToggleVehicleTypeCommandHandler(repo, uow, bus, dossier_port)
    cmd = ToggleVehicleTypeCommand(
        vehicle_id=vehicle.id,
        new_price=Decimal("0.00"),
    )
    with pytest.raises(DomainError):
        await handler.handle(cmd)
    assert len(repo.saved_vehicles) == 0
    assert len(bus.published_events) == 0


@pytest.mark.asyncio
async def test_toggle_active_dossier_without_bypass_raises_exception() -> None:
    vehicle = create_test_vehicle(CatalogType.SALE)
    repo = FakeVehicleRepository([vehicle])
    uow = FakeUnitOfWork()
    bus = FakeEventBus()
    dossier_port = FakeDossierExistencePort(has_active=True)
    handler = ToggleVehicleTypeCommandHandler(repo, uow, bus, dossier_port)
    cmd = ToggleVehicleTypeCommand(
        vehicle_id=vehicle.id,
        new_price=Decimal("600.00"),
        bypass_warning=False,
    )
    with pytest.raises(ActiveDossierWarningException) as exc_info:
        await handler.handle(cmd)
    assert exc_info.value.vehicle_id == vehicle.id
    assert len(repo.saved_vehicles) == 0
    assert len(bus.published_events) == 0


@pytest.mark.asyncio
async def test_toggle_active_dossier_with_bypass_succeeds() -> None:
    vehicle = create_test_vehicle(CatalogType.SALE)
    repo = FakeVehicleRepository([vehicle])
    uow = FakeUnitOfWork()
    bus = FakeEventBus()
    dossier_port = FakeDossierExistencePort(has_active=True)
    handler = ToggleVehicleTypeCommandHandler(repo, uow, bus, dossier_port)
    cmd = ToggleVehicleTypeCommand(
        vehicle_id=vehicle.id,
        new_price=Decimal("600.00"),
        bypass_warning=True,
    )
    result = await handler.handle(cmd)
    assert result.catalog_type == CatalogType.RENTAL
    assert len(bus.published_events) == 1


@pytest.mark.asyncio
async def test_toggle_no_active_dossier_with_bypass_succeeds() -> None:
    vehicle = create_test_vehicle(CatalogType.SALE)
    repo = FakeVehicleRepository([vehicle])
    uow = FakeUnitOfWork()
    bus = FakeEventBus()
    dossier_port = FakeDossierExistencePort(has_active=False)
    handler = ToggleVehicleTypeCommandHandler(repo, uow, bus, dossier_port)
    cmd = ToggleVehicleTypeCommand(
        vehicle_id=vehicle.id,
        new_price=Decimal("600.00"),
        bypass_warning=True,
    )
    result = await handler.handle(cmd)
    assert result.catalog_type == CatalogType.RENTAL
    assert len(bus.published_events) == 1
