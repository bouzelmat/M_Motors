from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.vehicles.domain.entities.vehicle import Vehicle
from src.vehicles.domain.value_objects.catalog_type import CatalogType
from src.vehicles.domain.value_objects.energy_type import EnergyType
from src.vehicles.domain.value_objects.mileage import Mileage
from src.vehicles.domain.value_objects.price import Price
from src.vehicles.domain.value_objects.vehicle_search_criteria import (
    VehicleSearchCriteria,
)
from src.vehicles.domain.value_objects.vehicle_status import VehicleStatus
from src.vehicles.infrastructure.repositories.SQLAlchemyVehicleRepository import (
    SQLAlchemyVehicleRepository,
)


@pytest.mark.asyncio
async def test_save_and_find_by_id(db_session: AsyncSession):
    """Vérifie l'enregistrement d'un véhicule puis sa récupération par identifiant."""

    repo = SQLAlchemyVehicleRepository(db_session)

    vehicle_id = uuid4()

    vehicle = Vehicle(
        id=vehicle_id,
        brand="Peugeot",
        model="208",
        year=2023,
        price=Price(20000.0),
        mileage=Mileage(10000),
        energy_type=EnergyType.ESSENCE,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.RENTAL,
        monthly_rent=Price(350.0),
        description="Voiture compacte",
    )

    await repo.save(vehicle)

    # Commit pour rendre les données visibles
    await db_session.commit()

    found = await repo.find_by_id(vehicle_id)

    assert found is not None
    assert found.id == vehicle_id
    assert found.brand == "Peugeot"
    assert found.monthly_rent is not None
    assert found.monthly_rent.value == 350.0


@pytest.mark.asyncio
async def test_find_by_criteria_rental(db_session: AsyncSession):
    """Vérifie la recherche de véhicules selon différents critères."""

    repo = SQLAlchemyVehicleRepository(db_session)

    # Insertion des données de test
    vehicles = [
        Vehicle(
            id=uuid4(),
            brand="A",
            model="A1",
            year=2022,
            price=Price(15000.0),
            mileage=Mileage(20000),
            energy_type=EnergyType.DIESEL,
            status=VehicleStatus.AVAILABLE,
            catalog_type=CatalogType.RENTAL,
            monthly_rent=Price(300.0),
        ),
        Vehicle(
            id=uuid4(),
            brand="B",
            model="B1",
            year=2022,
            price=Price(25000.0),
            mileage=Mileage(5000),
            energy_type=EnergyType.ELECTRIQUE,
            status=VehicleStatus.AVAILABLE,
            catalog_type=CatalogType.RENTAL,
            monthly_rent=Price(400.0),
        ),
        Vehicle(
            id=uuid4(),
            brand="C",
            model="C1",
            year=2021,
            price=Price(18000.0),
            mileage=Mileage(30000),
            energy_type=EnergyType.ESSENCE,
            status=VehicleStatus.AVAILABLE,
            catalog_type=CatalogType.SALE,
        ),
    ]

    for vehicle in vehicles:
        await repo.save(vehicle)

    await db_session.commit()

    # Recherche des locations avec un loyer maximal de 350 €
    criteria = VehicleSearchCriteria(
        mode="rental",
        max_monthly_rent=350.0,
    )

    results = await repo.find_by_criteria(criteria)

    assert len(results) == 1
    assert results[0].monthly_rent is not None
    assert results[0].monthly_rent.value == 300.0

    # Recherche de toutes les locations
    criteria = VehicleSearchCriteria(mode="rental")

    results = await repo.find_by_criteria(criteria)

    assert len(results) == 2

    # Recherche des véhicules à la vente
    criteria = VehicleSearchCriteria(mode="sale")  # <-- correction : mode='sale'

    results = await repo.find_by_criteria(criteria)

    assert len(results) == 1
    assert results[0].catalog_type == CatalogType.SALE
