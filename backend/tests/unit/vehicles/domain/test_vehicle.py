"""Tests unitaires pour l'association des services au véhicule."""

from decimal import Decimal
from uuid import uuid4
from datetime import datetime, timezone
import pytest

from src.vehicles.domain.entities.vehicle import Vehicle
from src.shared.domain.exceptions import DomainError
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


def test_vehicle_create_success() -> None:
    """Given des données valides, When Vehicle.create() est appelé, Then l'instance est créée avec status = AVAILABLE."""
    vehicle = Vehicle.create(
        brand="Peugeot",
        model="208",
        year=2024,
        price=Price(Decimal("18000.00")),
        mileage=Mileage(10000),
        energy_type=EnergyType.ESSENCE,
        catalog_type=CatalogType.SALE,
    )

    assert vehicle.id is not None
    assert vehicle.brand == "Peugeot"
    assert vehicle.model == "208"
    assert vehicle.status == VehicleStatus.AVAILABLE
    assert vehicle.catalog_type == CatalogType.SALE


def test_vehicle_create_missing_price_for_sale_raises_domain_error() -> None:
    """Given catalog_type = SALE sans prix de vente, When Vehicle.create() est appelé, Then une DomainError est levée."""
    with pytest.raises(DomainError, match="Un véhicule en vente doit avoir un prix"):
        Vehicle.create(
            brand="Renault",
            model="Clio",
            year=2023,
            price=None,
            mileage=Mileage(5000),
            energy_type=EnergyType.DIESEL,
            catalog_type=CatalogType.SALE,
        )


def test_vehicle_create_missing_monthly_rent_for_rental_raises_domain_error() -> None:
    """Given catalog_type = RENTAL sans monthly_rent, When Vehicle.create() est appelé, Then une DomainError est levée."""
    with pytest.raises(
        DomainError, match="Un véhicule en location doit avoir un loyer mensuel"
    ):
        Vehicle.create(
            brand="Tesla",
            model="Model 3",
            year=2024,
            price=Price(Decimal("40000.00")),
            mileage=Mileage(2000),
            energy_type=EnergyType.ELECTRIQUE,
            catalog_type=CatalogType.RENTAL,
            monthly_rent=None,
        )


def test_vehicle_create_negative_mileage_raises_domain_error() -> None:
    """Given mileage < 0, When Vehicle.create() est appelé, Then une DomainError est levée."""
    with pytest.raises((DomainError, ValueError)):
        Vehicle.create(
            brand="BMW",
            model="Série 3",
            year=2022,
            price=Price(Decimal("30000.00")),
            mileage=Mileage(-100),
            energy_type=EnergyType.DIESEL,
            catalog_type=CatalogType.SALE,
        )


def test_vehicle_create_invalid_year_raises_domain_error() -> None:
    """Given année invalide (< 1886 ou > année_courante + 1), When Vehicle.create() est appelé, Then une DomainError est levée."""
    current_year = datetime.now(timezone.utc).year

    with pytest.raises(DomainError):
        Vehicle.create(
            brand="Audi",
            model="A4",
            year=1800,
            price=Price(Decimal("25000.00")),
            mileage=Mileage(1000),
            energy_type=EnergyType.ESSENCE,
            catalog_type=CatalogType.SALE,
        )

    with pytest.raises(DomainError):
        Vehicle.create(
            brand="Audi",
            model="A4",
            year=current_year + 5,
            price=Price(Decimal("25000.00")),
            mileage=Mileage(1000),
            energy_type=EnergyType.ESSENCE,
            catalog_type=CatalogType.SALE,
        )


def test_switch_to_rental_success() -> None:
    """Passage du mode vente au mode location : efface le prix, met à jour le loyer et catalog_type."""
    vehicle = Vehicle(
        id=uuid4(),
        brand="Peugeot",
        model="208",
        year=2024,
        price=Price(Decimal("18000.00")),
        mileage=Mileage(10000),
        energy_type=EnergyType.ESSENCE,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.SALE,
    )
    new_rent = Price(Decimal("350.00"))

    updated_vehicle = vehicle.switch_to_rental(monthly_rent=new_rent)

    assert updated_vehicle.catalog_type == CatalogType.RENTAL
    assert updated_vehicle.monthly_rent == new_rent
    assert updated_vehicle.price is None
    assert updated_vehicle.status == vehicle.status
    assert updated_vehicle.id == vehicle.id
    # Vérification de l'immutabilité
    assert vehicle.catalog_type == CatalogType.SALE
    assert vehicle.price == Price(Decimal("18000.00"))


def test_switch_to_sale_success() -> None:
    """Passage du mode location au mode vente : efface le loyer, met à jour le prix et catalog_type."""
    vehicle = Vehicle(
        id=uuid4(),
        brand="Renault",
        model="Clio",
        year=2023,
        price=None,
        monthly_rent=Price(Decimal("300.00")),
        mileage=Mileage(15000),
        energy_type=EnergyType.DIESEL,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.RENTAL,
    )
    new_price = Price(Decimal("16000.00"))

    updated_vehicle = vehicle.switch_to_sale(price=new_price)

    assert updated_vehicle.catalog_type == CatalogType.SALE
    assert updated_vehicle.price == new_price
    assert updated_vehicle.monthly_rent is None
    assert updated_vehicle.status == vehicle.status
    assert updated_vehicle.id == vehicle.id
    # Vérification de l'immutabilité
    assert vehicle.catalog_type == CatalogType.RENTAL
    assert vehicle.monthly_rent == Price(Decimal("300.00"))


def test_switch_to_rental_already_rental_raises_domain_error() -> None:
    """Tentative de passage en mode location alors que le véhicule est déjà RENTAL."""
    vehicle = Vehicle(
        id=uuid4(),
        brand="Tesla",
        model="Model 3",
        year=2024,
        price=None,
        monthly_rent=Price(Decimal("600.00")),
        mileage=Mileage(5000),
        energy_type=EnergyType.ELECTRIQUE,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.RENTAL,
    )

    with pytest.raises(DomainError, match="Le véhicule est déjà en mode location."):
        vehicle.switch_to_rental(monthly_rent=Price(Decimal("650.00")))


def test_switch_to_sale_already_sale_raises_domain_error() -> None:
    """Tentative de passage en mode vente alors que le véhicule est déjà SALE."""
    vehicle = Vehicle(
        id=uuid4(),
        brand="BMW",
        model="Série 1",
        year=2022,
        price=Price(Decimal("22000.00")),
        mileage=Mileage(25000),
        energy_type=EnergyType.ESSENCE,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.SALE,
    )

    with pytest.raises(DomainError, match="Le véhicule est déjà en mode vente."):
        vehicle.switch_to_sale(price=Price(Decimal("21000.00")))


def test_switch_to_rental_invalid_rent_raises_domain_error() -> None:
    """Vérifie le rejet d'un loyer nul ou négatif lors du passage en location."""
    vehicle = Vehicle(
        id=uuid4(),
        brand="Audi",
        model="A3",
        year=2023,
        price=Price(Decimal("25000.00")),
        mileage=Mileage(12000),
        energy_type=EnergyType.ESSENCE,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.SALE,
    )

    with pytest.raises(DomainError):
        vehicle.switch_to_rental(monthly_rent=Price(Decimal("0.00")))

    with pytest.raises(DomainError):
        vehicle.switch_to_rental(monthly_rent=Price(Decimal("-100.00")))


def test_switch_to_sale_invalid_price_raises_domain_error() -> None:
    """Vérifie le rejet d'un prix nul ou négatif lors du passage en vente."""
    vehicle = Vehicle(
        id=uuid4(),
        brand="Fiat",
        model="500",
        year=2021,
        price=None,
        monthly_rent=Price(Decimal("200.00")),
        mileage=Mileage(30000),
        energy_type=EnergyType.ESSENCE,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.RENTAL,
    )

    with pytest.raises(DomainError):
        vehicle.switch_to_sale(price=Price(Decimal("0.00")))

    with pytest.raises(DomainError):
        vehicle.switch_to_sale(price=Price(Decimal("-5000.00")))
