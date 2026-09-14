"""Dependency providers for the Vehicles bounded context."""

from fastapi import Depends

from src.shared.infrastructure.dependencies import SessionDep
from src.shared.infrastructure.messaging.in_memory_event_bus import (
    InMemoryEventBus,
)
from src.shared.infrastructure.persistence.sqlalchemy_uow import (
    SqlAlchemyUnitOfWork,
)
from src.vehicles.application.commands.add_vehicle import (
    AddVehicleCommandHandler,
)
from src.vehicles.application.queries.get_rental_catalog_query import (
    GetRentalCatalogQueryHandler,
)
from src.vehicles.application.queries.get_vehicle_detail_query import (
    GetVehicleDetailQueryHandler,
)
from src.vehicles.application.queries.search_vehicles_query import (
    SearchVehiclesQueryHandler,
)
from src.vehicles.infrastructure.repositories.sqlalchemy_vehicle_repository import (
    SQLAlchemyVehicleRepository,
)
from src.vehicles.infrastructure.storage.s3_storage_service import S3StorageService


async def get_vehicle_repository(
    session: SessionDep,
) -> SQLAlchemyVehicleRepository:
    """Return the vehicle repository."""
    return SQLAlchemyVehicleRepository(session)


def get_storage_service() -> S3StorageService:
    return S3StorageService()


async def get_vehicle_detail_handler(
    repository: SQLAlchemyVehicleRepository = Depends(get_vehicle_repository),
) -> GetVehicleDetailQueryHandler:
    return GetVehicleDetailQueryHandler(repository)


async def get_search_vehicles_query_handler(
    repository: SQLAlchemyVehicleRepository = Depends(get_vehicle_repository),
) -> SearchVehiclesQueryHandler:
    """Return the generic vehicle search query handler."""
    return SearchVehiclesQueryHandler(repository)


async def get_rental_catalog_query_handler(
    session: SessionDep,
) -> GetRentalCatalogQueryHandler:
    """Return the rental catalog query handler."""
    repository = SQLAlchemyVehicleRepository(session)
    return GetRentalCatalogQueryHandler(repository)


async def get_add_vehicle_command_handler(
    session: SessionDep,
) -> AddVehicleCommandHandler:
    """Return the add vehicle command handler."""
    repository = SQLAlchemyVehicleRepository(session)
    uow = SqlAlchemyUnitOfWork(session)
    event_bus = InMemoryEventBus()
    return AddVehicleCommandHandler(
        repository=repository,
        uow=uow,
        event_bus=event_bus,
    )
