"""Seed de données de test pour les tests E2E du catalogue et du conflit 409."""

import asyncio
import sys
from pathlib import Path
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

# Ajoute la racine du backend au PYTHONPATH pour permettre les imports src.*
BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from src.auth.domain.value_objects import Role
from src.auth.infrastructure.orm.user_model import UserModel
from src.dossiers.domain.value_objects.dossier_status import DossierStatus
from src.dossiers.infrastructure.orm.dossier_model import DossierModel
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

ACTIVE_DOSSIER_ID = UUID("20000000-0000-0000-0000-000000000001")
TEST_USER_ID = UUID("30000000-0000-0000-0000-000000000001")
TEST_USER_EMAIL = "client.seed@example.com"


async def ensure_test_user(session: AsyncSession) -> UUID:
    """Garantit la présence d'un utilisateur de test stable avec le rôle CLIENT."""
    stmt = select(UserModel).where(UserModel.id == TEST_USER_ID)
    result = await session.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user is None:
        test_user = UserModel(
            id=TEST_USER_ID,
            email=TEST_USER_EMAIL,
            hashed_password="$2b$12$eImiTXuWVxfM37uY4JANjOL.s8Q3e2Dsc4wXGjA1m6j/b5N8rYmxe",  # Hash factice de test
            first_name="Client",
            last_name="Seed",
            role=Role.CLIENT,
            is_active=True,
        )
        session.add(test_user)
        await session.flush()

    return TEST_USER_ID


async def seed_active_dossier(
    session: AsyncSession,
    vehicle_id: UUID,
    user_id: UUID,
) -> None:
    """Crée le dossier actif utilisé par les tests de conflit 409."""
    # Suppression ciblée du dossier fixe s'il existe déjà
    await session.execute(
        delete(DossierModel).where(DossierModel.id == ACTIVE_DOSSIER_ID)
    )

    active_dossier = DossierModel(
        id=ACTIVE_DOSSIER_ID,
        user_id=user_id,
        vehicle_id=vehicle_id,
        status=DossierStatus.SUBMITTED,
        upload_started_at=None,
    )
    session.add(active_dossier)


async def _populate_seed_data(session: AsyncSession) -> None:
    """Moteur interne exécutant les requêtes d'insertion et de nettoyage dans une session donnée."""
    # Nettoyage ordonné des tables pour respecter l'intégrité référentielle
    await session.execute(
        delete(DossierModel).where(
            DossierModel.vehicle_id.in_([PEUGEOT_ID, RENAULT_ID, TESLA_ID])
        )
    )
    await session.execute(delete(VehicleServiceAssociation))
    await session.execute(delete(ServiceModel))
    await session.execute(delete(VehicleModel))

    # Garantir l'utilisateur de test stable
    user_id = await ensure_test_user(session)

    # Création des services disponibles
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

    # Création des véhicules
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
                ServiceInclusion(
                    service_id=ASSISTANCE_ID,
                    name="Assistance",
                    monthly_cost=10,
                    category=ServiceCategory.ASSISTANCE,
                    included=False,
                ),
            ],
        ),
    ]

    repository = SQLAlchemyVehicleRepository(session)
    for vehicle in vehicles:
        await repository.save(vehicle)

    # Création du dossier actif lié à la Renault
    await seed_active_dossier(session, vehicle_id=RENAULT_ID, user_id=user_id)


async def seed_vehicles(session: AsyncSession | None = None) -> None:
    """Réinitialise et insère les données nécessaires aux tests E2E et au conflit 409.

    - Si une session est transmise (ex: test Pytest), réutilise la transaction courante sans commit.
    - Sinon (ex: execution standalone CLI), instancie une session autonome et valide la transaction.
    """
    if session is not None:
        await _populate_seed_data(session)
        await session.flush()
    else:
        session_factory = get_session_factory()
        async with session_factory() as standalone_session:
            await _populate_seed_data(standalone_session)
            await standalone_session.commit()


if __name__ == "__main__":
    asyncio.run(seed_vehicles())
