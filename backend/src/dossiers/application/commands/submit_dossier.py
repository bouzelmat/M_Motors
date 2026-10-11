"""Commande applicative de soumission d'un dossier client."""

from dataclasses import dataclass
from uuid import UUID

from src.dossiers.domain.exceptions import DossierAccessDeniedException
from src.dossiers.domain.ports.document_repository import DocumentRepository
from src.dossiers.domain.ports.dossier_repository import DossierRepository
from src.dossiers.domain.value_objects.document_status import DocumentStatus
from src.shared.domain.exceptions import DomainError, NotFoundError
from src.shared.domain.ports.unit_of_work import AbstractUnitOfWork


@dataclass(frozen=True)
class SubmitDossierCommand:
    dossier_id: UUID
    user_id: UUID


class SubmitDossierCommandHandler:
    """Vérifie les pièces requises et soumet le dossier dans une transaction."""

    def __init__(
        self,
        dossier_repository: DossierRepository,
        document_repository: DocumentRepository,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._dossier_repository = dossier_repository
        self._document_repository = document_repository
        self._uow = uow

    async def handle(self, command: SubmitDossierCommand):
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

            documents = await self._document_repository.find_by_dossier(dossier.id)
            uploaded_types = {
                document.type.value
                for document in documents
                if document.status
                in (DocumentStatus.UPLOADED, DocumentStatus.VALIDATED)
            }
            requested_types = set(dossier.requested_document_types or [])
            if not uploaded_types or not requested_types.issubset(uploaded_types):
                raise DomainError(
                    "Au moins un justificatif téléversé est requis et tous les documents demandés doivent être fournis."
                )

            submitted_dossier = dossier.submit()
            await self._dossier_repository.save(submitted_dossier)
            await self._uow.commit()

        return submitted_dossier
