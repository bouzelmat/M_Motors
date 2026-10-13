"""Cas d'usage : consulter les dossiers archivés."""

from src.dossiers.application.queries.list_dossier_history import (
    ListDossierHistoryQuery,
)
from src.dossiers.application.queries.read_models import PendingDossierReadModel
from src.dossiers.application.ports.dossier_read_repository import (
    DossierReadRepository,
)


class ListDossierHistoryUseCase:
    """Orchestre la récupération des dossiers clôturés."""

    def __init__(self, dossier_repository: DossierReadRepository) -> None:
        self._dossier_repository = dossier_repository

    async def execute(
        self, _query: ListDossierHistoryQuery
    ) -> list[PendingDossierReadModel]:
        return await self._dossier_repository.list_history()
