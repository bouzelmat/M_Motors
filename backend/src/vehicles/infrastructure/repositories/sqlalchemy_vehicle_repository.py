import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.vehicles.domain.entities.vehicle import Vehicle
from src.vehicles.domain.entities.vehicle_photo import VehiclePhoto
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
    ServiceModel,
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
        statement = (
            select(VehicleModel)
            .where(VehicleModel.id == vehicle.id)
            .options(
                selectinload(VehicleModel.service_associations).selectinload(
                    VehicleServiceAssociation.service
                )
            )
        )
        result = await self._session.execute(statement)
        existing = result.scalar_one_or_none()

        if existing:
            self._mapper.to_orm(vehicle, existing_orm=existing)
        else:
            self._session.add(self._mapper.to_orm(vehicle))

        await self._session.flush()

    async def find_by_id(self, vehicle_id: UUID) -> Vehicle | None:
        stmt = (
            select(VehicleModel)
            .where(VehicleModel.id == vehicle_id)
            .options(
                selectinload(VehicleModel.service_associations).selectinload(
                    VehicleServiceAssociation.service
                ),
                selectinload(VehicleModel.photos),
            )
        )

        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()

        if orm is None:
            return None

        return self._mapper.to_domain(orm)

    async def list_all(self) -> list[Vehicle]:
        statement = (
            select(VehicleModel)
            .options(
                selectinload(VehicleModel.service_associations).selectinload(
                    VehicleServiceAssociation.service
                ),
                selectinload(VehicleModel.photos),
            )
            .order_by(VehicleModel.brand, VehicleModel.model)
        )
        result = await self._session.execute(statement)
        return [self._mapper.to_domain(orm) for orm in result.scalars().all()]

    async def delete_by_id(self, vehicle_id: UUID) -> bool:
        orm = await self._session.get(VehicleModel, vehicle_id)
        if orm is None:
            return False
        await self._session.delete(orm)
        await self._session.flush()
        return True

    async def find_by_id_for_update(self, vehicle_id: UUID) -> Vehicle | None:
        stmt = (
            select(VehicleModel)
            .where(VehicleModel.id == vehicle_id)
            .options(
                selectinload(VehicleModel.service_associations).selectinload(
                    VehicleServiceAssociation.service
                ),
                selectinload(VehicleModel.photos),
            )
            .with_for_update()
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._mapper.to_domain(orm) if orm is not None else None

    async def find_by_criteria(
        self,
        criteria: VehicleSearchCriteria,
    ) -> list[Vehicle]:
        """Retourne les véhicules correspondant aux critères de recherche."""

        stmt = select(VehicleModel).options(
            selectinload(VehicleModel.service_associations).selectinload(
                VehicleServiceAssociation.service
            ),
            selectinload(VehicleModel.photos),
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

    async def list_service_catalog(self) -> list[ServiceInclusion]:
        """Retourne les services du catalogue dans un ordre stable."""
        result = await self._session.execute(
            select(ServiceModel).order_by(ServiceModel.category, ServiceModel.name)
        )
        return [
            ServiceInclusion(
                service_id=service.id,
                name=service.name,
                monthly_cost=service.monthly_cost,
                category=service.category,
                included=False,
            )
            for service in result.scalars().all()
        ]

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
                ),
                selectinload(VehicleModel.photos),  # ✅ AJOUTÉ : Charger les photos
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
        # ✅ CORRIGÉ : photo_url supprimé
        content_type: str,
        uploaded_by: UUID,
    ) -> VehiclePhotoModel:
        """Reserve a photo key until the direct S3 upload is confirmed."""
        photo = VehiclePhotoModel(
            vehicle_id=vehicle_id,
            object_key=object_key,
            # ✅ CORRIGÉ : photo_url supprimé
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

    async def list_uploaded_photos(self, vehicle_id: UUID) -> list[VehiclePhoto]:
        statement = (
            select(VehiclePhotoModel)
            .where(
                VehiclePhotoModel.vehicle_id == vehicle_id,
                VehiclePhotoModel.is_uploaded.is_(True),
            )
            .order_by(VehiclePhotoModel.created_at, VehiclePhotoModel.id)
        )
        result = await self._session.execute(statement)
        return [
            VehiclePhoto(
                id=photo.id,
                vehicle_id=photo.vehicle_id,
                object_key=photo.object_key,
                is_primary=photo.is_primary,
                created_at=photo.created_at,
                uploaded_at=photo.uploaded_at,
            )
            for photo in result.scalars().all()
        ]

    async def set_primary_photo(self, vehicle_id: UUID, photo_id: UUID) -> bool:
        statement = select(VehiclePhotoModel).where(
            VehiclePhotoModel.vehicle_id == vehicle_id,
            VehiclePhotoModel.id == photo_id,
            VehiclePhotoModel.is_uploaded.is_(True),
        )
        result = await self._session.execute(statement)
        photo = result.scalar_one_or_none()
        if photo is None:
            return False

        await self._session.execute(
            update(VehiclePhotoModel)
            .where(VehiclePhotoModel.vehicle_id == vehicle_id)
            .values(is_primary=False)
        )
        photo.is_primary = True
        await self._session.flush()
        return True

    async def delete_photo(self, vehicle_id: UUID, photo_id: UUID) -> str | None:
        statement = select(VehiclePhotoModel).where(
            VehiclePhotoModel.vehicle_id == vehicle_id,
            VehiclePhotoModel.id == photo_id,
        )
        result = await self._session.execute(statement)
        photo = result.scalar_one_or_none()
        if photo is None:
            return None

        object_key = photo.object_key
        was_primary = photo.is_primary
        await self._session.delete(photo)
        await self._session.flush()

        if was_primary:
            next_photo_statement = (
                select(VehiclePhotoModel)
                .where(
                    VehiclePhotoModel.vehicle_id == vehicle_id,
                    VehiclePhotoModel.is_uploaded.is_(True),
                )
                .order_by(VehiclePhotoModel.created_at, VehiclePhotoModel.id)
                .limit(1)
            )
            next_photo_result = await self._session.execute(next_photo_statement)
            next_photo = next_photo_result.scalar_one_or_none()
            if next_photo is not None:
                next_photo.is_primary = True
                await self._session.flush()

        return object_key
