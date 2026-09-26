"""Commande applicative de validation d'un dossier par un administrateur."""

from dataclasses import dataclass
from uuid import UUID
from src.dossiers.domain.entities.dossier import Dossier
from src.dossiers.domain.events.dossier_validated import DossierValidated
from src.dossiers.domain.ports.dossier_repository import DossierRepository
from src.shared.domain.exceptions import NotFoundError
from src.shared.domain.ports.event_bus import AbstractEventBus
from src.shared.domain.ports.unit_of_work import AbstractUnitOfWork


@dataclass(frozen=True)
class ValidateDossierCommand:
    """Données nécessaires à la validation d'un dossier."""

    dossier_id: UUID
    admin_id: UUID
    comment: str | None = None


class ValidateDossierCommandHandler:
    """Valide un dossier et publie l'événement correspondant."""

    def __init__(
        self,
        dossier_repository: DossierRepository,
        uow: AbstractUnitOfWork,
        event_bus: AbstractEventBus,
    ) -> None:
        self._dossier_repository = dossier_repository
        self._uow = uow
        self._event_bus = event_bus

    async def handle(self, command: ValidateDossierCommand) -> Dossier:
        """Valide un dossier SUBMITTED et publie DossierValidated."""
        async with self._uow:
            dossier = await self._dossier_repository.get_by_id(command.dossier_id)
            if dossier is None:
                raise NotFoundError(
                    f"Dossier avec l'identifiant {command.dossier_id} introuvable."
                )

            validated_dossier = dossier.approve(
                admin_id=command.admin_id,
                comment=command.comment,
            )
            await self._dossier_repository.save(validated_dossier)

            event = DossierValidated(
                dossier_id=validated_dossier.id,
                admin_id=command.admin_id,
                comment=command.comment,
            )
            await self._event_bus.publish(event)

            await self._uow.commit()

        return validated_dossier
