"""Adaptateur d'infrastructure vérifiant l'existence de dossiers actifs pour un véhicule."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dossiers.domain.ports.dossier_existence_port import DossierExistencePort
from src.dossiers.domain.value_objects.dossier_status import DossierStatus
from src.dossiers.infrastructure.models.dossier_model import DossierModel


class DossierExistenceAdapter(DossierExistencePort):
    """Adaptateur inter-domaines exécutant la vérification d'activité en SQL via la session courante."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def has_active_dossier_for_vehicle(
        self,
        vehicle_id: UUID,
    ) -> bool:
        """Exécute une requête EXISTS filtrée sur les statuts DRAFT et SUBMITTED."""
        active_statuses = (
            DossierStatus.DRAFT,
            DossierStatus.SUBMITTED,
            DossierStatus.DOCUMENTS_PENDING,
        )

        stmt = select(
            select(DossierModel.id)
            .where(
                DossierModel.vehicle_id == vehicle_id,
                DossierModel.status.in_(active_statuses),
            )
            .exists()
        )

        result = await self._session.scalar(stmt)
        return bool(result)
