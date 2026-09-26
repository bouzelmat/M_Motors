"""Commande applicative de demande de documents complémentaires."""

from dataclasses import dataclass
from uuid import UUID
from src.dossiers.domain.entities.dossier import Dossier
from src.dossiers.domain.events.documents_requested import DocumentsRequested
from src.dossiers.domain.ports.dossier_repository import DossierRepository
from src.shared.domain.exceptions import NotFoundError
from src.shared.domain.ports.event_bus import AbstractEventBus
from src.shared.domain.ports.unit_of_work import AbstractUnitOfWork


@dataclass(frozen=True)
class RequestDocumentsCommand:
    """Données nécessaires à la demande de documents complémentaires."""

    dossier_id: UUID
    admin_id: UUID
    document_types: list[str]


class RequestDocumentsCommandHandler:
    """Demande des documents complémentaires et publie l'événement correspondant."""

    def __init__(
        self,
        dossier_repository: DossierRepository,
        uow: AbstractUnitOfWork,
        event_bus: AbstractEventBus,
    ) -> None:
        self._dossier_repository = dossier_repository
        self._uow = uow
        self._event_bus = event_bus

    async def handle(self, command: RequestDocumentsCommand) -> Dossier:
        """Demande des documents pour un dossier SUBMITTED ou DOCUMENTS_PENDING."""
        async with self._uow:
            dossier = await self._dossier_repository.get_by_id(command.dossier_id)
            if dossier is None:
                raise NotFoundError(
                    f"Dossier avec l'identifiant {command.dossier_id} introuvable."
                )

            updated_dossier = dossier.request_documents(
                document_types=command.document_types,
            )
            await self._dossier_repository.save(updated_dossier)

            event = DocumentsRequested(
                dossier_id=updated_dossier.id,
                admin_id=command.admin_id,
                document_types=command.document_types,
            )
            await self._event_bus.publish(event)

            await self._uow.commit()

        return updated_dossier
