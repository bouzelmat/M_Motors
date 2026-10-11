"""Commande applicative d'annulation d'un dossier en préparation."""

from dataclasses import dataclass
from uuid import UUID

from src.dossiers.domain.entities.dossier import Dossier
from src.dossiers.domain.exceptions import DossierAccessDeniedException
from src.dossiers.domain.ports.dossier_repository import DossierRepository
from src.shared.domain.exceptions import NotFoundError
from src.shared.domain.ports.unit_of_work import AbstractUnitOfWork


@dataclass(frozen=True)
class CancelDossierCommand:
    """Identifie le dossier et son propriétaire lors de l'annulation."""

    dossier_id: UUID
    user_id: UUID


class CancelDossierCommandHandler:
    """Annule un dossier DRAFT appartenant au client connecté."""

    def __init__(
        self,
        dossier_repository: DossierRepository,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._dossier_repository = dossier_repository
        self._uow = uow

    async def handle(self, command: CancelDossierCommand) -> Dossier:
        """Vérifie le propriétaire et persiste l'annulation atomiquement."""
        async with self._uow:
            dossier = await self._dossier_repository.get_by_id_for_update(
                command.dossier_id
            )
            if dossier is None:
                raise NotFoundError(f"Dossier {command.dossier_id} introuvable.")
            if not dossier.is_owned_by(command.user_id):
                raise DossierAccessDeniedException(
                    "Vous n'êtes pas propriétaire de ce dossier."
                )

            cancelled_dossier = dossier.cancel()
            await self._dossier_repository.save(cancelled_dossier)
            await self._uow.commit()

        return cancelled_dossier
