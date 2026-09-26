"""Requête applicative permettant de récupérer le statut d'un dossier."""

from dataclasses import dataclass
from uuid import UUID

from src.dossiers.domain.entities.dossier import Dossier
from src.dossiers.domain.ports.dossier_repository import DossierRepository


@dataclass(frozen=True, slots=True)
class GetDossierStatusQuery:
    """Requête de lecture du statut d'un dossier."""

    dossier_id: UUID


class GetDossierStatusQueryHandler:
    """Traite la lecture du statut et de la date de mise à jour du dossier."""

    def __init__(self, dossier_repository: DossierRepository) -> None:
        self._dossier_repository = dossier_repository

    async def handle(self, query: GetDossierStatusQuery) -> Dossier | None:
        """Retourne le dossier demandé ou None s'il est introuvable."""

        return await self._dossier_repository.get_by_id(query.dossier_id)
