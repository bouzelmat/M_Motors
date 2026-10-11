import asyncio
import os
from uuid import uuid4

import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.dossiers.application.commands.create_dossier import (
    CreateDossierCommand,
    CreateDossierCommandHandler,
)
from src.dossiers.domain.exceptions import VehicleNotAvailableException
from src.dossiers.infrastructure.models.dossier_model import DossierModel
from src.dossiers.infrastructure.repository.sqlalchemy_dossier_repository import (
    SQLAlchemyDossierRepository,
)
from src.shared.infrastructure.messaging.in_memory_event_bus import InMemoryEventBus
from src.shared.infrastructure.persistence.sqlalchemy_uow import SqlAlchemyUnitOfWork
from src.vehicles.domain.value_objects.catalog_type import CatalogType
from src.vehicles.domain.value_objects.energy_type import EnergyType
from src.vehicles.domain.value_objects.vehicle_status import VehicleStatus
from src.vehicles.infrastructure.orm.vehicle_model import VehicleModel
from src.vehicles.infrastructure.repositories.sqlalchemy_vehicle_repository import (
    SQLAlchemyVehicleRepository,
)


@pytest.mark.asyncio
async def test_concurrent_dossier_creation_reserves_vehicle_once() -> None:
    engine = create_async_engine(
        os.environ["DATABASE_URL"],
        poolclass=NullPool,
    )
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    vehicle_id = uuid4()
    try:
        async with session_factory() as setup_session:
            setup_session.add(
                VehicleModel(
                    id=vehicle_id,
                    brand="Test",
                    model="Concurrent",
                    year=2025,
                    price=25000,
                    mileage=1000,
                    energy_type=EnergyType.ESSENCE,
                    status=VehicleStatus.AVAILABLE,
                    catalog_type=CatalogType.SALE,
                )
            )
            await setup_session.commit()

        async def create_for(user_id):
            async with session_factory() as session:
                handler = CreateDossierCommandHandler(
                    dossier_repository=SQLAlchemyDossierRepository(session),
                    vehicle_repository=SQLAlchemyVehicleRepository(session),
                    uow=SqlAlchemyUnitOfWork(session),
                    event_bus=InMemoryEventBus(),
                )
                try:
                    return await handler.handle(
                        CreateDossierCommand(user_id=user_id, vehicle_id=vehicle_id)
                    )
                except VehicleNotAvailableException:
                    return None

        outcomes = await asyncio.gather(create_for(uuid4()), create_for(uuid4()))
        assert sum(outcome is not None for outcome in outcomes) == 1

    finally:
        async with session_factory() as cleanup_session:
            await cleanup_session.execute(
                delete(DossierModel).where(DossierModel.vehicle_id == vehicle_id)
            )
            await cleanup_session.execute(
                delete(VehicleModel).where(VehicleModel.id == vehicle_id)
            )
            await cleanup_session.commit()
        await engine.dispose()
