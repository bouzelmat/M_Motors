import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.vehicles.domain.entities.vehicle import Vehicle
from src.vehicles.domain.ports.vehicle_repository import VehicleRepository
from src.vehicles.domain.value_objects.catalog_type import CatalogType
from src.vehicles.domain.value_objects.service_inclusion import ServiceInclusion
from src.vehicles.domain.value_objects.vehicle_search_criteria import (
    VehicleSearchCriteria,
)
from src.vehicles.domain.value_objects.vehicle_status import VehicleStatus
from src.vehicles.infrastructure.mappers.service_mapper import ServiceMapper
from src.vehicles.infrastructure.mappers.vehicle_mapper import VehicleMapper
from src.vehicles.infrastructure.orm.service_model import (
    VehicleServiceAssociation,
)
from src.vehicles.infrastructure.orm.vehicle_model import VehicleModel
from src.vehicles.infrastructure.orm.vehicle_photo_model import VehiclePhotoModel

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

        stmt = select(VehicleModel).options(
            selectinload(VehicleModel.service_associations).selectinload(
                VehicleServiceAssociation.service
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
                    VehicleModel.monthly_rent <= criteria.max_monthly_rent,
                )

        elif criteria.mode == "sale":
            conditions.append(
                VehicleModel.catalog_type == CatalogType.SALE.value,
            )

            # Filtre spécifique à la vente.
            if criteria.max_price is not None:
                conditions.append(
                    VehicleModel.price <= criteria.max_price,
                )

        else:
            raise ValueError(f"Mode de recherche non supporté : {criteria.mode}")

        # Filtres optionnels communs aux deux modes.
        if criteria.brand is not None:
            conditions.append(
                VehicleModel.brand.ilike(f"%{criteria.brand}%"),
            )

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

    async def create_pending_photo(
        self,
        vehicle_id: UUID,
        object_key: str,
        photo_url: str,
        content_type: str,
        uploaded_by: UUID,
    ) -> VehiclePhotoModel:
        """Reserve a photo key until the direct S3 upload is confirmed."""
        photo = VehiclePhotoModel(
            vehicle_id=vehicle_id,
            object_key=object_key,
            photo_url=photo_url,
            content_type=content_type,
            uploaded_by=uploaded_by,
        )
        self._session.add(photo)
        await self._session.flush()
        return photo

    async def get_photo(
        self,
        vehicle_id: UUID,
        photo_id: UUID,
    ) -> VehiclePhotoModel | None:
        statement = select(VehiclePhotoModel).where(
            VehiclePhotoModel.id == photo_id,
            VehiclePhotoModel.vehicle_id == vehicle_id,
        )
        result = await self._session.execute(statement)
        return result.scalar_one_or_none()

    async def confirm_photo(self, photo: VehiclePhotoModel) -> None:
        """Mark an uploaded photo as visible and make the first one primary."""
        photo.is_uploaded = True
        photo.uploaded_at = datetime.now(timezone.utc)

        primary_statement = select(VehiclePhotoModel).where(
            VehiclePhotoModel.vehicle_id == photo.vehicle_id,
            VehiclePhotoModel.is_uploaded.is_(True),
            VehiclePhotoModel.is_primary.is_(True),
            VehiclePhotoModel.id != photo.id,
        )
        result = await self._session.execute(primary_statement)
        if result.scalar_one_or_none() is None:
            photo.is_primary = True

        await self._session.flush()
