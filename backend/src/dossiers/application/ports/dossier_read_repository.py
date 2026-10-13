"""Application port for dossier read-model queries."""

from typing import Protocol

from src.dossiers.application.queries.read_models import PendingDossierReadModel


class DossierReadRepository(Protocol):
    """Port for administrative dossier projections."""

    async def list_pending(
        self,
        sort_by: str = "submitted_at",
    ) -> list[PendingDossierReadModel]: ...

    async def list_history(self) -> list[PendingDossierReadModel]: ...
