"""Seed des données utilisées par les tests End-to-End Playwright."""

from decimal import Decimal
from uuid import uuid4

from sqlalchemy import delete

from src.shared.infrastructure.database import get_session
from src.vehicles.domain.entities.vehicle import Vehicle
from src.vehicles.domain.value_objects.catalog_type import CatalogType
from src.vehicles.domain.value_objects.energy_type import EnergyType
from src.vehicles.domain.value_objects.mileage import Mileage
from src.vehicles.domain.value_objects.price import Price
from src.vehicles.domain.value_objects.service_category import ServiceCategory
from src.vehicles.domain.value_objects.service_inclusion import ServiceInclusion
from src.vehicles.domain.value_objects.vehicle_status import VehicleStatus
from src.vehicles.infrastructure.orm.service_model import ServiceModel
from src.vehicles.infrastructure.orm.vehicle_model import VehicleModel
from src.vehicles.infrastructure.repositories.sqlalchemy_vehicle_repository import (
    SQLAlchemyVehicleRepository,
)


async def seed_catalog() -> None:
    """Réinitialise puis insère les véhicules utilisés par les tests E2E."""

    async for session in get_session():
        # Nettoyage des anciennes données
        await session.execute(delete(VehicleModel))
        await session.execute(delete(ServiceModel))

        # Services utilisés par les tests E2E
        assurance_id = uuid4()
        entretien_id = uuid4()

        assurance = ServiceModel(
            id=assurance_id,
            name="Assurance tous risques",
            monthly_cost=Decimal("50.00"),
            category=ServiceCategory.INSURANCE,
        )

        entretien = ServiceModel(
            id=entretien_id,
            name="Entretien et SAV",
            monthly_cost=Decimal("30.00"),
            category=ServiceCategory.MAINTENANCE,
        )

        session.add_all([assurance, entretien])
        await session.flush()

        repository = SQLAlchemyVehicleRepository(session)

        vehicles = [
            Vehicle(
                id=uuid4(),
                brand="Peugeot",
                model="208",
                year=2023,
                price=Price(20000),
                mileage=Mileage(12000),
                energy_type=EnergyType.ESSENCE,
                status=VehicleStatus.AVAILABLE,
                catalog_type=CatalogType.RENTAL,
                monthly_rent=Price(350),
                description="Citadine compacte idéale pour la ville.",
                services=[
                    ServiceInclusion(
                        service_id=assurance_id,
                        name="Assurance tous risques",
                        monthly_cost=Decimal("50.00"),
                        category=ServiceCategory.INSURANCE,
                        included=True,
                    ),
                    ServiceInclusion(
                        service_id=entretien_id,
                        name="Entretien et SAV",
                        monthly_cost=Decimal("30.00"),
                        category=ServiceCategory.MAINTENANCE,
                        included=False,
                    ),
                ],
            ),
            Vehicle(
                id=uuid4(),
                brand="Renault",
                model="Clio",
                year=2022,
                price=Price(18000),
                mileage=Mileage(15000),
                energy_type=EnergyType.DIESEL,
                status=VehicleStatus.AVAILABLE,
                catalog_type=CatalogType.RENTAL,
                monthly_rent=Price(400),
                description="Polyvalente et économique.",
                services=[],
            ),
            Vehicle(
                id=uuid4(),
                brand="Tesla",
                model="Model 3",
                year=2023,
                price=Price(45000),
                mileage=Mileage(5000),
                energy_type=EnergyType.ELECTRIQUE,
                status=VehicleStatus.AVAILABLE,
                catalog_type=CatalogType.RENTAL,
                monthly_rent=Price(650),
                description="Berline électrique premium.",
                services=[],
            ),
        ]

        for vehicle in vehicles:
            await repository.save(vehicle)

        await session.commit()

        print("Catalogue Playwright initialisé.")

        break
