import logging
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.vehicles.domain.entities.vehicle import Vehicle
from src.vehicles.domain.value_objects.catalog_type import CatalogType
from src.vehicles.domain.value_objects.service_inclusion import ServiceInclusion
from src.vehicles.domain.value_objects.vehicle_search_criteria import (
    VehicleSearchCriteria,
)
from src.vehicles.domain.value_objects.vehicle_status import VehicleStatus
from src.vehicles.domain.ports.vehicle_repository import VehicleRepository
from src.vehicles.infrastructure.mappers.service_mapper import ServiceMapper
from src.vehicles.infrastructure.mappers.vehicle_mapper import VehicleMapper
from src.vehicles.infrastructure.orm.service_model import (
    VehicleServiceAssociation,
)
from src.vehicles.infrastructure.orm.vehicle_model import VehicleModel

logger = logging.getLogger(__name__)


class SQLAlchemyVehicleRepository(VehicleRepository):
    """Adaptateur SQLAlchemy pour le repository véhicules."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._mapper = VehicleMapper()
        self._service_mapper = ServiceMapper()

    async def save(self, vehicle: Vehicle) -> None:
        orm = self._mapper.to_orm(vehicle)

        # Si l'ID existe déjà, on récupère l'existant.
        existing = await self._session.get(VehicleModel, vehicle.id)

        if existing:
            self._mapper.to_orm(vehicle, existing_orm=existing)
        else:
            self._session.add(orm)

        await self._session.flush()

    async def find_by_id(self, vehicle_id: UUID) -> Vehicle | None:
        stmt = (
            select(VehicleModel)
            .where(VehicleModel.id == vehicle_id)
            .options(
                selectinload(VehicleModel.service_associations).selectinload(
                    VehicleServiceAssociation.service
                )
            )
        )

        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()

        if orm is None:
            return None

        return self._mapper.to_domain(orm)

    async def find_by_criteria(
        self,
        criteria: VehicleSearchCriteria,
    ) -> list[Vehicle]:
        """Retourne les véhicules correspondant aux critères de recherche."""

        stmt = (
            select(VehicleModel)
            .options(
                selectinload(VehicleModel.service_associations).selectinload(
                    VehicleServiceAssociation.service
                )
            )
        )

        # Uniquement les véhicules disponibles.
        conditions = [
            VehicleModel.status == VehicleStatus.AVAILABLE.value,
        ]

        # Filtrage obligatoire selon le mode du catalogue.
        if criteria.mode == "rental":
            conditions.append(
                VehicleModel.catalog_type == CatalogType.RENTAL.value,
            )

            # Filtre spécifique à la location.
            if criteria.max_monthly_rent is not None:
                conditions.append(
                    VehicleModel.monthly_rent
                    <= criteria.max_monthly_rent,
                )

        elif criteria.mode == "sale":
            conditions.append(
                VehicleModel.catalog_type == CatalogType.SALE.value,
            )

            # Filtre spécifique à la vente.
            # Le modèle ORM utilise "price" et non "sale_price".
            if criteria.max_price is not None:
                conditions.append(
                    VehicleModel.price <= criteria.max_price,
                )

        else:
            raise ValueError(
                f"Mode de recherche non supporté : {criteria.mode}"
            )

        # Filtres optionnels communs aux deux modes.

        # Recherche partielle insensible à la casse.
        if criteria.brand is not None:
            conditions.append(
                VehicleModel.brand.ilike(f"%{criteria.brand}%"),
            )

        # Le modèle ORM utilise "energy_type" et non "fuel_type".
        if criteria.fuel_type is not None:
            conditions.append(
                VehicleModel.energy_type == criteria.fuel_type,
            )

        if criteria.max_mileage is not None:
            conditions.append(
                VehicleModel.mileage <= criteria.max_mileage,
            )

        stmt = stmt.where(and_(*conditions))

        result = await self._session.execute(stmt)
        orms = result.scalars().all()

        return [self._mapper.to_domain(orm) for orm in orms]

    async def find_by_id_with_services(
        self,
        vehicle_id: UUID,
    ) -> tuple[Vehicle, list[ServiceInclusion]] | None:
        """Retourne un véhicule avec ses services et leur statut d'inclusion."""

        statement = (
            select(VehicleModel)
            .where(VehicleModel.id == vehicle_id)
            .options(
                selectinload(VehicleModel.service_associations).selectinload(
                    VehicleServiceAssociation.service
                )
            )
        )

        result = await self._session.execute(statement)
        vehicle_model = result.scalar_one_or_none()

        if vehicle_model is None:
            return None

        vehicle = self._mapper.to_domain(vehicle_model)

        return vehicle, vehicle.services
