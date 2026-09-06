from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.vehicles.domain.entities.vehicle import Vehicle
from src.vehicles.domain.value_objects.catalog_type import CatalogType
from src.vehicles.domain.value_objects.energy_type import EnergyType
from src.vehicles.domain.value_objects.mileage import Mileage
from src.vehicles.domain.value_objects.price import Price
from src.vehicles.domain.value_objects.service_category import ServiceCategory
from src.vehicles.domain.value_objects.vehicle_search_criteria import (
    VehicleSearchCriteria,
)
from src.vehicles.domain.value_objects.vehicle_status import VehicleStatus
from src.vehicles.infrastructure.orm.service_model import (
    ServiceModel,
    VehicleServiceAssociation,
)
from src.vehicles.infrastructure.repositories.sqlalchemy_vehicle_repository import (
    SQLAlchemyVehicleRepository,
)


@pytest.mark.asyncio
async def test_save_and_find_by_id(db_session: AsyncSession) -> None:
    """Vérifie la sauvegarde et la récupération d'un véhicule par ID."""
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
        catalog_type=CatalogType.SALE,
    )

    await repo.save(vehicle)
    await db_session.commit()

    saved_vehicle = await repo.find_by_id(vehicle.id)

    assert saved_vehicle is not None
    assert saved_vehicle.id == vehicle.id
    assert saved_vehicle.brand == "Peugeot"
    assert saved_vehicle.model == "208"


@pytest.mark.asyncio
async def test_find_by_id_loads_services_with_inclusion(
    db_session: AsyncSession,
) -> None:
    """Vérifie que find_by_id charge les services et leur statut d'inclusion."""
    repo = SQLAlchemyVehicleRepository(db_session)

    vehicle_id = uuid4()
    service_id = uuid4()

    vehicle = Vehicle(
        id=vehicle_id,
        brand="Peugeot",
        model="308",
        year=2024,
        price=Price(25000.0),
        mileage=Mileage(10000),
        energy_type=EnergyType.ESSENCE,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.RENTAL,
        monthly_rent=Price(399.0),
    )

    await repo.save(vehicle)

    service = ServiceModel(
        id=service_id,
        name="Assurance tous risques",
        monthly_cost=Decimal("49.90"),
        category=ServiceCategory.INSURANCE,
    )

    association = VehicleServiceAssociation(
        vehicle_id=vehicle_id,
        service_id=service_id,
        included=True,
        service=service,
    )

    db_session.add_all([service, association])
    await db_session.commit()

    loaded_vehicle = await repo.find_by_id(vehicle_id)

    assert loaded_vehicle is not None
    assert len(loaded_vehicle.services) == 1
    assert loaded_vehicle.services[0].service_id == service_id
    assert loaded_vehicle.services[0].included is True


@pytest.mark.asyncio
async def test_find_by_id_preserves_excluded_service(
    db_session: AsyncSession,
) -> None:
    """Vérifie qu'un service non inclus est correctement chargé avec included=False."""
    repo = SQLAlchemyVehicleRepository(db_session)

    vehicle_id = uuid4()
    service_id = uuid4()

    vehicle = Vehicle(
        id=vehicle_id,
        brand="Renault",
        model="Clio",
        year=2023,
        price=Price(18000.0),
        mileage=Mileage(15000),
        energy_type=EnergyType.DIESEL,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.RENTAL,
        monthly_rent=Price(299.0),
    )

    await repo.save(vehicle)

    service = ServiceModel(
        id=service_id,
        name="Entretien annuel",
        monthly_cost=Decimal("19.90"),
        category=ServiceCategory.MAINTENANCE,
    )

    association = VehicleServiceAssociation(
        vehicle_id=vehicle_id,
        service_id=service_id,
        included=False,
        service=service,
    )

    db_session.add_all([service, association])
    await db_session.commit()

    loaded_vehicle = await repo.find_by_id(vehicle_id)

    assert loaded_vehicle is not None
    assert len(loaded_vehicle.services) == 1
    assert loaded_vehicle.services[0].included is False


@pytest.mark.asyncio
async def test_find_by_id_loads_multiple_services_with_inclusion(
    db_session: AsyncSession,
) -> None:
    """Vérifie le chargement de plusieurs services avec des statuts d'inclusion différents."""
    repo = SQLAlchemyVehicleRepository(db_session)

    vehicle_id = uuid4()
    service_1_id = uuid4()
    service_2_id = uuid4()

    vehicle = Vehicle(
        id=vehicle_id,
        brand="BMW",
        model="Série 1",
        year=2024,
        price=Price(35000.0),
        mileage=Mileage(5000),
        energy_type=EnergyType.ESSENCE,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.RENTAL,
        monthly_rent=Price(499.0),
    )

    await repo.save(vehicle)

    service_1 = ServiceModel(
        id=service_1_id,
        name="Assistance",
        monthly_cost=Decimal("15.00"),
        category=ServiceCategory.ASSISTANCE,
    )

    service_2 = ServiceModel(
        id=service_2_id,
        name="Extension de garantie",
        monthly_cost=Decimal("29.90"),
        category=ServiceCategory.MAINTENANCE,
    )

    association_1 = VehicleServiceAssociation(
        vehicle_id=vehicle_id,
        service_id=service_1_id,
        included=True,
        service=service_1,
    )

    association_2 = VehicleServiceAssociation(
        vehicle_id=vehicle_id,
        service_id=service_2_id,
        included=False,
        service=service_2,
    )

    db_session.add_all([service_1, service_2, association_1, association_2])
    await db_session.commit()

    loaded_vehicle = await repo.find_by_id(vehicle_id)

    assert loaded_vehicle is not None
    assert len(loaded_vehicle.services) == 2

    services_by_id = {s.service_id: s for s in loaded_vehicle.services}

    assert services_by_id[service_1_id].included is True
    assert services_by_id[service_2_id].included is False


@pytest.mark.asyncio
async def test_find_by_criteria_rental(db_session: AsyncSession) -> None:
    """Vérifie le filtrage des véhicules par critères en mode location."""
    repo = SQLAlchemyVehicleRepository(db_session)

    v1 = Vehicle(
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

    v2 = Vehicle(
        id=uuid4(),
        brand="Renault",
        model="Clio",
        year=2022,
        price=Price(18000.0),
        mileage=Mileage(20000),
        energy_type=EnergyType.DIESEL,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.RENTAL,
        monthly_rent=Price(400.0),
    )

    await repo.save(v1)
    await repo.save(v2)
    await db_session.commit()

    criteria = VehicleSearchCriteria(mode="rental", max_monthly_rent=350.0)
    results = await repo.find_by_criteria(criteria)

    assert len(results) == 1
    assert results[0].brand == "Peugeot"