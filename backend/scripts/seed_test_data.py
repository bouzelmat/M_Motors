"""Seed de données de test pour les tests E2E du catalogue."""

import asyncio
import sys
from pathlib import Path
from uuid import uuid4

# Ajoute la racine du backend au PYTHONPATH pour permettre les imports src.*
BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from src.shared.infrastructure.database import get_session_factory
from src.vehicles.domain.entities.Vehicle import Vehicle
from src.vehicles.domain.value_objects.CatalogType import CatalogType
from src.vehicles.domain.value_objects.EnergyType import EnergyType
from src.vehicles.domain.value_objects.Mileage import Mileage
from src.vehicles.domain.value_objects.Price import Price
from src.vehicles.domain.value_objects.VehicleStatus import VehicleStatus
from src.vehicles.infrastructure.repositories.SQLAlchemyVehicleRepository import (
    SQLAlchemyVehicleRepository,
)


async def seed_vehicles() -> None:
    """Insère les véhicules nécessaires aux tests E2E du catalogue."""

    session_factory = get_session_factory()

    async with session_factory() as session:
        repository = SQLAlchemyVehicleRepository(session)

        vehicles = [
            Vehicle(
                id=uuid4(),
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
            ),
            Vehicle(
                id=uuid4(),
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
            ),
            Vehicle(
                id=uuid4(),
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
            ),
        ]

        for vehicle in vehicles:
            await repository.save(vehicle)

        await session.commit()

    print("Données E2E du catalogue insérées avec succès.")


if __name__ == "__main__":
    asyncio.run(seed_vehicles())
