"""Cas d'usage : Consulter la liste des dossiers de financement en attente de validation."""

from src.dossiers.application.queries.list_pending_dossiers import (
    ListPendingDossiersQuery,
)
from src.dossiers.application.queries.read_models import PendingDossierReadModel
from src.dossiers.domain.ports.dossier_repository import DossierRepository


class ListPendingDossiersUseCase:
    """Orchestre la récupération optimisée des dossiers en attente."""

    def __init__(self, dossier_repository: DossierRepository) -> None:
        self._dossier_repository = dossier_repository

    async def execute(
        self,
        query: ListPendingDossiersQuery,
    ) -> list[PendingDossierReadModel]:
        """Exécute la requête de lecture des dossiers en attente."""
        return await self._dossier_repository.list_pending(sort_by=query.sort_by)
