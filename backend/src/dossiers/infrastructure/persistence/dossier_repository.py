"""Adaptateur SQLAlchemy implémentant la persistance des dossiers."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.dossiers.domain.entities.dossier import Dossier
from src.dossiers.domain.ports.dossier_repository import DossierRepository
from src.dossiers.domain.value_objects.dossier_status import DossierStatus
from src.dossiers.infrastructure.models.dossier_model import DossierModel
from src.dossiers.infrastructure.persistence.mappers import DossierMapper


class SQLAlchemyDossierRepository(DossierRepository):
    """Adaptateur SQLAlchemy pour le repository des dossiers."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, dossier_id: UUID) -> Dossier | None:
        """Récupère un dossier par son identifiant avec ses relations eager loaded."""
        statement = (
            select(DossierModel)
            .options(
                joinedload(DossierModel.trade_in),
                joinedload(DossierModel.financing_plan),
            )
            .where(DossierModel.id == dossier_id)
        )
        result = await self._session.execute(statement)
        model = result.unique().scalar_one_or_none()

        if model is None:
            return None
        return DossierMapper.to_domain(model)

    async def save(self, dossier: Dossier) -> None:
        """Insère ou met à jour un dossier et ses relations puis synchronise la session."""
        statement = (
            select(DossierModel)
            .options(
                joinedload(DossierModel.trade_in),
                joinedload(DossierModel.financing_plan),
            )
            .where(DossierModel.id == dossier.id)
        )
        result = await self._session.execute(statement)
        existing_model = result.unique().scalar_one_or_none()

        model = DossierMapper.to_orm(dossier, existing_model)

        if existing_model is None:
            self._session.add(model)

        await self._session.flush()

    async def get_stale_draft_dossiers(
        self,
        cutoff_time: datetime,
    ) -> list[Dossier]:
        """Récupère les brouillons dont le premier upload est arrivé à échéance."""
        statement = (
            select(DossierModel)
            .options(
                joinedload(DossierModel.trade_in),
                joinedload(DossierModel.financing_plan),
            )
            .where(
                DossierModel.status == DossierStatus.DRAFT,
                DossierModel.upload_started_at.is_not(None),
                DossierModel.upload_started_at <= cutoff_time,
            )
        )
        result = await self._session.execute(statement)
        return [
            DossierMapper.to_domain(model)
            for model in result.unique().scalars().all()
        ]

    async def has_active_for_vehicle(self, vehicle_id: UUID) -> bool:
        """Indique si un véhicule possède un dossier DRAFT ou SUBMITTED."""
        statement = select(DossierModel.id).where(
            DossierModel.vehicle_id == vehicle_id,
            DossierModel.status.in_((DossierStatus.DRAFT, DossierStatus.SUBMITTED)),
        )
        result = await self._session.execute(statement)
        return result.scalar_one_or_none() is not None