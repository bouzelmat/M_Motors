"""Implémentation SQLAlchemy de la persistance des dossiers."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload  # <-- AJOUT POUR REGLER LE MISSINGGREENLET

from src.auth.infrastructure.orm.user_model import UserModel
from src.dossiers.application.constants import PENDING_STATUSES
from src.dossiers.application.queries.read_models import PendingDossierReadModel
from src.dossiers.domain.entities.dossier import Dossier
from src.dossiers.domain.ports.dossier_repository import DossierRepository
from src.dossiers.infrastructure.mapper.dossier_mapper import DossierMapper
from src.dossiers.infrastructure.models.dossier_model import DossierModel
from src.shared.domain.exceptions import DomainError
from src.vehicles.infrastructure.orm.vehicle_model import VehicleModel


class SQLAlchemyDossierRepository(DossierRepository):
    """Adaptateur de dépôt pour les dossiers utilisant SQLAlchemy."""

    ALLOWED_SORT_FIELDS = {
        "submitted_at": DossierModel.submitted_at,
        "created_at": DossierModel.created_at,
        "updated_at": DossierModel.updated_at,
    }

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, dossier_id: UUID) -> Dossier | None:
        stmt = (
            select(DossierModel)
            .where(DossierModel.id == dossier_id)
            .options(
                selectinload(DossierModel.trade_in),
                selectinload(DossierModel.financing_plan),
            )
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return DossierMapper.to_domain(model) if model else None

    async def list_by_user(self, user_id: UUID) -> list[Dossier]:
        stmt = (
            select(DossierModel)
            .where(DossierModel.user_id == user_id)
            .options(
                selectinload(DossierModel.trade_in),
                selectinload(DossierModel.financing_plan),
            )
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [DossierMapper.to_domain(m) for m in models]

    async def save(self, dossier: Dossier) -> None:
        stmt = select(DossierModel).where(DossierModel.id == dossier.id)
        result = await self._session.execute(stmt)
        existing_model = result.scalar_one_or_none()

        model = DossierMapper.to_orm(dossier, existing_model=existing_model)
        if existing_model is None:
            self._session.add(model)

    async def get_stale_draft_dossiers(
        self,
        cutoff_time: datetime,
    ) -> list[Dossier]:
        stmt = (
            select(DossierModel)
            .where(
                DossierModel.status == DossierModel.status.type.enum_class.DRAFT,
                DossierModel.upload_started_at.is_not(None),
                DossierModel.upload_started_at < cutoff_time,
            )
            .options(
                selectinload(DossierModel.trade_in),
                selectinload(DossierModel.financing_plan),
            )
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [DossierMapper.to_domain(m) for m in models]

    async def has_active_for_vehicle(self, vehicle_id: UUID) -> bool:
        stmt = select(DossierModel).where(
            DossierModel.vehicle_id == vehicle_id,
            DossierModel.status.in_(
                [
                    DossierModel.status.type.enum_class.DRAFT,
                    DossierModel.status.type.enum_class.SUBMITTED,
                ]
            ),
        )
        result = await self._session.execute(stmt)
        return result.first() is not None

    async def find_rejected_since(self, days: int) -> list[Dossier]:
        stmt = (
            select(DossierModel)
            .where(
                DossierModel.status == DossierModel.status.type.enum_class.REJECTED,
                DossierModel.rejected_at.is_not(None),
            )
            .options(
                selectinload(DossierModel.trade_in),
                selectinload(DossierModel.financing_plan),
            )
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [
            d
            for m in models
            if (d := DossierMapper.to_domain(m)).is_rejected_since(days)
        ]

    async def list_pending(
        self,
        sort_by: str = "submitted_at",
    ) -> list[PendingDossierReadModel]:
        if sort_by not in self.ALLOWED_SORT_FIELDS:
            raise DomainError(f"Champ de tri invalide : '{sort_by}'")

        sort_column = self.ALLOWED_SORT_FIELDS[sort_by]

        stmt = (
            select(
                DossierModel.id,
                DossierModel.user_id,
                UserModel.email.label("client_email"),
                DossierModel.vehicle_id,
                VehicleModel.brand.label("vehicle_brand"),
                VehicleModel.model.label("vehicle_model"),
                DossierModel.status,
                DossierModel.submitted_at,
                DossierModel.created_at,
                DossierModel.updated_at,
            )
            .join(UserModel, UserModel.id == DossierModel.user_id)
            .join(VehicleModel, VehicleModel.id == DossierModel.vehicle_id)
            .where(DossierModel.status.in_(PENDING_STATUSES))
            .order_by(sort_column.desc().nulls_last())
        )

        result = await self._session.execute(stmt)
        rows = result.mappings().all()

        return [
            PendingDossierReadModel(
                id=row["id"],
                user_id=row["user_id"],
                client_email=row["client_email"],
                vehicle_id=row["vehicle_id"],
                vehicle_brand=row["vehicle_brand"],
                vehicle_model=row["vehicle_model"],
                status=row["status"],
                submitted_at=row["submitted_at"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]
