"""Requête applicative pour lister les dossiers d'un utilisateur."""

from dataclasses import dataclass
from uuid import UUID

from src.dossiers.domain.entities.dossier import Dossier
from src.dossiers.domain.ports.dossier_repository import DossierRepository


@dataclass(frozen=True, slots=True)
class ListUserDossiersQuery:
    """Requête de lecture des dossiers appartenant à un utilisateur."""

    user_id: UUID


class ListUserDossiersQueryHandler:
    """Traite la récupération de la liste des dossiers d'un utilisateur."""

    def __init__(self, dossier_repository: DossierRepository) -> None:
        self._dossier_repository = dossier_repository

    async def handle(self, query: ListUserDossiersQuery) -> list[Dossier]:
        """Retourne les dossiers appartenant à l'utilisateur demandé."""

        return await self._dossier_repository.list_by_user(query.user_id)
