"""Cas d'usage : consulter les dossiers archivés."""

from src.dossiers.application.queries.list_dossier_history import (
    ListDossierHistoryQuery,
)
from src.dossiers.application.queries.read_models import PendingDossierReadModel
from src.dossiers.domain.ports.dossier_repository import DossierRepository


class ListDossierHistoryUseCase:
    """Orchestre la récupération des dossiers clôturés."""

    def __init__(self, dossier_repository: DossierRepository) -> None:
        self._dossier_repository = dossier_repository

    async def execute(
        self, _query: ListDossierHistoryQuery
    ) -> list[PendingDossierReadModel]:
        return await self._dossier_repository.list_history()
