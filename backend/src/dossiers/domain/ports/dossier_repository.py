"""Interface de persistance des dossiers."""

from datetime import datetime
from typing import Protocol
from uuid import UUID

from src.dossiers.domain.entities.dossier import Dossier


class DossierRepository(Protocol):
    """Port secondaire pour l'accès aux dossiers."""

    async def get_by_id(self, dossier_id: UUID) -> Dossier | None: ...

    async def list_by_user(self, user_id: UUID) -> list[Dossier]: ...

    async def save(self, dossier: Dossier) -> None: ...

    async def get_stale_draft_dossiers(
        self,
        cutoff_time: datetime,
    ) -> list[Dossier]:
        """Récupère les dossiers DRAFT dont upload_started_at est antérieur à cutoff_time."""
        ...

    async def has_active_for_vehicle(self, vehicle_id: UUID) -> bool:
        """Vérifie s'il existe au moins un dossier actif (DRAFT ou SUBMITTED) pour un véhicule donné."""
        ...
