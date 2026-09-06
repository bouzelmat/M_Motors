"""Tests unitaires pour l'association des services au véhicule."""

from decimal import Decimal
from uuid import uuid4

from src.vehicles.domain.entities.vehicle import Vehicle
from src.vehicles.domain.value_objects.catalog_type import CatalogType
from src.vehicles.domain.value_objects.energy_type import EnergyType
from src.vehicles.domain.value_objects.mileage import Mileage
from src.vehicles.domain.value_objects.price import Price
from src.vehicles.domain.value_objects.service_category import ServiceCategory
from src.vehicles.domain.value_objects.service_inclusion import ServiceInclusion
from src.vehicles.domain.value_objects.vehicle_status import VehicleStatus


def test_vehicle_contains_services_with_inclusion_status() -> None:
    """Verify that services are attached to the vehicle with their inclusion status."""

    service_id = uuid4()

    service = ServiceInclusion(
        service_id=service_id,
        name="Assurance tous risques",
        monthly_cost=Decimal("49.90"),
        category=ServiceCategory.INSURANCE,
        included=True,
    )

    vehicle = Vehicle(
        id=uuid4(),
        brand="Peugeot",
        model="208",
        year=2024,
        price=Price(Decimal("18000.00")),
        mileage=Mileage(15000),
        energy_type=EnergyType.ESSENCE,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.SALE,
        services=[service],
    )

    services = vehicle.get_services_with_inclusion()

    assert len(services) == 1
    assert services[0].service_id == service_id
    assert services[0].name == "Assurance tous risques"
    assert services[0].monthly_cost == Decimal("49.90")
    assert services[0].category == ServiceCategory.INSURANCE
    assert services[0].included is True

def test_vehicle_has_empty_services_by_default() -> None:
    """Verify that a vehicle created without explicit services defaults to an empty list."""
    vehicle = Vehicle(
        id=uuid4(),
        brand="Renault",
        model="Clio",
        year=2023,
        price=Price(Decimal("15000.00")),
        mileage=Mileage(20000),
        energy_type=EnergyType.DIESEL,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.SALE,
    )

    assert vehicle.get_services_with_inclusion() == []


def test_get_services_returns_defensive_copy() -> None:
    """Verify that mutating the returned services list does not alter the entity state."""
    service = ServiceInclusion(
        service_id=uuid4(),
        name="Assistance Panne",
        monthly_cost=Decimal("14.99"),
        category=ServiceCategory.ASSISTANCE,
        included=False,
    )

    vehicle = Vehicle(
        id=uuid4(),
        brand="Peugeot",
        model="208",
        year=2024,
        price=Price(Decimal("18000.00")),
        mileage=Mileage(15000),
        energy_type=EnergyType.ESSENCE,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.SALE,
        services=[service],
    )

    # Récupération et tentative de modification externe
    extracted_services = vehicle.get_services_with_inclusion()
    extracted_services.clear()

    # L'état de l'entité doit rester intact
    assert len(vehicle.get_services_with_inclusion()) == 1


def test_services_are_preserved_on_status_change() -> None:
    """Verify that state transition methods (e.g., mark_maintenance) keep attached services."""
    service = ServiceInclusion(
        service_id=uuid4(),
        name="Contrôle Technique",
        monthly_cost=Decimal("9.99"),
        category=ServiceCategory.INSPECTION,
        included=True,
    )

    vehicle = Vehicle(
        id=uuid4(),
        brand="Tesla",
        model="Model 3",
        year=2024,
        price=Price(Decimal("40000.00")),
        mileage=Mileage(5000),
        energy_type=EnergyType.ELECTRIQUE,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.SALE,
        services=[service],
    )

    updated_vehicle = vehicle.mark_maintenance()

    assert updated_vehicle.status == VehicleStatus.MAINTENANCE
    assert len(updated_vehicle.get_services_with_inclusion()) == 1
    assert updated_vehicle.get_services_with_inclusion()[0].name == "Contrôle Technique"