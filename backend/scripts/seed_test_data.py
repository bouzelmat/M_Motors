"""Seed de données de test pour les tests E2E du catalogue."""

import asyncio
import sys
from pathlib import Path
from uuid import UUID

from sqlalchemy import delete

# Ajoute la racine du backend au PYTHONPATH pour permettre les imports src.*
BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from src.shared.infrastructure.database import get_session_factory
from src.vehicles.domain.entities.vehicle import Vehicle
from src.vehicles.domain.value_objects.catalog_type import CatalogType
from src.vehicles.domain.value_objects.energy_type import EnergyType
from src.vehicles.domain.value_objects.mileage import Mileage
from src.vehicles.domain.value_objects.price import Price
from src.vehicles.domain.value_objects.service_inclusion import ServiceInclusion
from src.vehicles.domain.value_objects.service_category import ServiceCategory
from src.vehicles.domain.value_objects.vehicle_status import VehicleStatus
from src.vehicles.infrastructure.orm.service_model import (
    ServiceModel,
    VehicleServiceAssociation,
)
from src.vehicles.infrastructure.orm.vehicle_model import VehicleModel
from src.vehicles.infrastructure.repositories.sqlalchemy_vehicle_repository import (
    SQLAlchemyVehicleRepository,
)

# IDs fixes pour rendre le seed déterministe.
PEUGEOT_ID = UUID("00000000-0000-0000-0000-000000000001")
RENAULT_ID = UUID("00000000-0000-0000-0000-000000000002")
TESLA_ID = UUID("00000000-0000-0000-0000-000000000003")

ASSURANCE_ID = UUID("10000000-0000-0000-0000-000000000001")
ENTRETIEN_ID = UUID("10000000-0000-0000-0000-000000000002")
ASSISTANCE_ID = UUID("10000000-0000-0000-0000-000000000003")


async def seed_vehicles() -> None:
    """Réinitialise et insère les données nécessaires aux tests E2E."""
    session_factory = get_session_factory()

    async with session_factory() as session:
        # Nettoyage des associations avant les services et les véhicules.
        await session.execute(delete(VehicleServiceAssociation))
        await session.execute(delete(ServiceModel))
        await session.execute(delete(VehicleModel))

        # Création des services disponibles.
        services = [
            ServiceModel(
                id=ASSURANCE_ID,
                name="Assurance",
                monthly_cost=30,
                category=ServiceCategory.INSURANCE,
            ),
            ServiceModel(
                id=ENTRETIEN_ID,
                name="Entretien",
                monthly_cost=20,
                category=ServiceCategory.MAINTENANCE,
            ),
            ServiceModel(
                id=ASSISTANCE_ID,
                name="Assistance",
                monthly_cost=10,
                category=ServiceCategory.ASSISTANCE,
            ),
        ]

        session.add_all(services)

        # Création des véhicules avec leurs services.
        vehicles = [
            Vehicle(
                id=PEUGEOT_ID,
                brand="Peugeot",
                model="208",
                year=2023,
                price=Price(20000.0),
                mileage=Mileage(12000),
                energy_type=EnergyType.ESSENCE,
                status=VehicleStatus.AVAILABLE,
                catalog_type=CatalogType.RENTAL,
                monthly_rent=Price(350.0),
                description="Compacte et économique",
                services=[
                    ServiceInclusion(
                        service_id=ASSURANCE_ID,
                        name="Assurance",
                        monthly_cost=30,
                        category=ServiceCategory.INSURANCE,
                        included=True,
                    ),
                    ServiceInclusion(
                        service_id=ENTRETIEN_ID,
                        name="Entretien",
                        monthly_cost=20,
                        category=ServiceCategory.MAINTENANCE,
                        included=False,
                    ),
                    ServiceInclusion(
                        service_id=ASSISTANCE_ID,
                        name="Assistance",
                        monthly_cost=10,
                        category=ServiceCategory.ASSISTANCE,
                        included=False,
                    ),
                ],
            ),
            Vehicle(
                id=RENAULT_ID,
                brand="Renault",
                model="Clio",
                year=2022,
                price=Price(18000.0),
                mileage=Mileage(15000),
                energy_type=EnergyType.DIESEL,
                status=VehicleStatus.AVAILABLE,
                catalog_type=CatalogType.RENTAL,
                monthly_rent=Price(400.0),
                description="Citadine polyvalente",
                services=[
                    ServiceInclusion(
                        service_id=ASSURANCE_ID,
                        name="Assurance",
                        monthly_cost=30,
                        category=ServiceCategory.INSURANCE,
                        included=False,
                    ),
                    ServiceInclusion(
                        service_id=ENTRETIEN_ID,
                        name="Entretien",
                        monthly_cost=20,
                        category=ServiceCategory.MAINTENANCE,
                        included=False,
                    ),
                ],
            ),
            Vehicle(
                id=TESLA_ID,
                brand="Tesla",
                model="Model 3",
                year=2023,
                price=Price(45000.0),
                mileage=Mileage(5000),
                energy_type=EnergyType.ELECTRIQUE,
                status=VehicleStatus.AVAILABLE,
                catalog_type=CatalogType.RENTAL,
                monthly_rent=Price(650.0),
                description="Berline électrique premium",
                services=[
                    ServiceInclusion(
                        service_id=ASSISTANCE_ID,
                        name="Assistance",
                        monthly_cost=10,
                        category=ServiceCategory.ASSISTANCE,
                        included=True,
                    ),
                    ServiceInclusion(
                        service_id=ENTRETIEN_ID,
                        name="Entretien",
                        monthly_cost=20,
                        category=ServiceCategory.MAINTENANCE,
                        included=False,
                    ),
                ],
            ),
        ]

        repository = SQLAlchemyVehicleRepository(session)

        for vehicle in vehicles:
            await repository.save(vehicle)

        await session.commit()

    print("Données E2E du catalogue insérées avec succès.")


if __name__ == "__main__":
    asyncio.run(seed_vehicles())
