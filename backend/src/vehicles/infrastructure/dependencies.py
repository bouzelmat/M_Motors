"""Dependency providers for the Vehicles bounded context."""

from fastapi import Depends

from src.shared.infrastructure.dependencies import SessionDep
from src.vehicles.application.queries.get_rental_catalog_query import (
    GetRentalCatalogQueryHandler,
)
from src.vehicles.application.queries.get_vehicle_detail_query import (
    GetVehicleDetailQueryHandler,
)
from src.vehicles.infrastructure.repositories.sqlalchemy_vehicle_repository import (
    SQLAlchemyVehicleRepository,
)


async def get_vehicle_repository(
    session: SessionDep,
) -> SQLAlchemyVehicleRepository:
    """Return the vehicle repository."""

    return SQLAlchemyVehicleRepository(session)


async def get_vehicle_detail_handler(
    repository: SQLAlchemyVehicleRepository = Depends(get_vehicle_repository),
) -> GetVehicleDetailQueryHandler:
    return GetVehicleDetailQueryHandler(repository)


async def get_rental_catalog_query_handler(
    session: SessionDep,
) -> GetRentalCatalogQueryHandler:
    """Return the rental catalog query handler."""

    repository = SQLAlchemyVehicleRepository(session)

    return GetRentalCatalogQueryHandler(repository)
