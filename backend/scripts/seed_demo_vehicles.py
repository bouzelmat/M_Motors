"""Insère des véhicules de démonstration sans effacer les données existantes."""

import asyncio
import sys
from pathlib import Path
from uuid import UUID

from sqlalchemy import select

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from src.shared.infrastructure.database import get_session_factory
from src.vehicles.domain.entities.vehicle import Vehicle
from src.vehicles.domain.value_objects.catalog_type import CatalogType
from src.vehicles.domain.value_objects.energy_type import EnergyType
from src.vehicles.domain.value_objects.mileage import Mileage
from src.vehicles.domain.value_objects.price import Price
from src.vehicles.domain.value_objects.service_category import ServiceCategory
from src.vehicles.domain.value_objects.service_inclusion import ServiceInclusion
from src.vehicles.domain.value_objects.vehicle_status import VehicleStatus
from src.vehicles.infrastructure.orm.service_model import (
    ServiceModel,
    VehicleServiceAssociation,
)
from src.vehicles.infrastructure.repositories.sqlalchemy_vehicle_repository import (
    SQLAlchemyVehicleRepository,
)

DEMO_VEHICLES = (
    Vehicle(
        id=UUID("a1000000-0000-0000-0000-000000000001"),
        brand="Peugeot",
        model="208",
        year=2023,
        price=Price(19_900),
        mileage=Mileage(12_500),
        energy_type=EnergyType.ESSENCE,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.SALE,
        description="Citadine récente, idéale pour les trajets quotidiens.",
    ),
    Vehicle(
        id=UUID("a1000000-0000-0000-0000-000000000002"),
        brand="Renault",
        model="Captur",
        year=2022,
        price=Price(22_500),
        mileage=Mileage(28_000),
        energy_type=EnergyType.DIESEL,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.SALE,
        description="SUV compact confortable et polyvalent.",
    ),
    Vehicle(
        id=UUID("a1000000-0000-0000-0000-000000000003"),
        brand="Peugeot",
        model="2008",
        year=2024,
        price=None,
        mileage=Mileage(8_000),
        energy_type=EnergyType.ESSENCE,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.RENTAL,
        monthly_rent=Price(429),
        description="SUV récent proposé en location longue durée.",
        services=[
            ServiceInclusion(
                service_id=UUID("10000000-0000-0000-0000-000000000001"),
                name="Assurance",
                monthly_cost=30,
                category=ServiceCategory.INSURANCE,
                included=False,
            ),
            ServiceInclusion(
                service_id=UUID("10000000-0000-0000-0000-000000000002"),
                name="Entretien",
                monthly_cost=20,
                category=ServiceCategory.MAINTENANCE,
                included=False,
            ),
            ServiceInclusion(
                service_id=UUID("10000000-0000-0000-0000-000000000003"),
                name="Assistance",
                monthly_cost=10,
                category=ServiceCategory.ASSISTANCE,
                included=False,
            ),
        ],
    ),
    Vehicle(
        id=UUID("a1000000-0000-0000-0000-000000000004"),
        brand="Renault",
        model="Clio",
        year=2023,
        price=None,
        mileage=Mileage(10_000),
        energy_type=EnergyType.DIESEL,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.RENTAL,
        monthly_rent=Price(379),
        description="Citadine économique disponible en location.",
        services=[
            ServiceInclusion(
                service_id=UUID("10000000-0000-0000-0000-000000000001"),
                name="Assurance",
                monthly_cost=30,
                category=ServiceCategory.INSURANCE,
                included=False,
            ),
            ServiceInclusion(
                service_id=UUID("10000000-0000-0000-0000-000000000002"),
                name="Entretien",
                monthly_cost=20,
                category=ServiceCategory.MAINTENANCE,
                included=False,
            ),
            ServiceInclusion(
                service_id=UUID("10000000-0000-0000-0000-000000000003"),
                name="Assistance",
                monthly_cost=10,
                category=ServiceCategory.ASSISTANCE,
                included=False,
            ),
        ],
    ),
)


async def seed_demo_vehicles() -> None:
    """Insère les véhicules de démonstration absents du catalogue."""
    session_factory = get_session_factory()
    inserted_count = 0

    async with session_factory() as session:
        repository = SQLAlchemyVehicleRepository(session)
        default_services = (
            ServiceModel(
                id=UUID("10000000-0000-0000-0000-000000000001"),
                name="Assurance",
                monthly_cost=30,
                category=ServiceCategory.INSURANCE,
            ),
            ServiceModel(
                id=UUID("10000000-0000-0000-0000-000000000002"),
                name="Entretien",
                monthly_cost=20,
                category=ServiceCategory.MAINTENANCE,
            ),
            ServiceModel(
                id=UUID("10000000-0000-0000-0000-000000000003"),
                name="Assistance",
                monthly_cost=10,
                category=ServiceCategory.ASSISTANCE,
            ),
        )
        for service in default_services:
            if await session.get(ServiceModel, service.id) is None:
                session.add(service)
        await session.flush()

        for vehicle in DEMO_VEHICLES:
            existing_vehicle = await repository.find_by_id(vehicle.id)
            if existing_vehicle is None:
                await repository.save(vehicle)
                inserted_count += 1
                continue

            existing_service_ids = set(
                (
                    await session.scalars(
                        select(VehicleServiceAssociation.service_id).where(
                            VehicleServiceAssociation.vehicle_id == vehicle.id
                        )
                    )
                ).all()
            )
            for service in vehicle.services:
                if service.service_id not in existing_service_ids:
                    session.add(
                        VehicleServiceAssociation(
                            vehicle_id=vehicle.id,
                            service_id=service.service_id,
                            included=service.included,
                        )
                    )

        await session.commit()

    print(f"Seed catalogue terminé : {inserted_count} véhicule(s) ajouté(s).")


if __name__ == "__main__":
    asyncio.run(seed_demo_vehicles())
