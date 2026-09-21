"""Cas d'usage de confirmation du téléversement d'un document."""

from dataclasses import dataclass
from uuid import UUID

from src.dossiers.domain.entities.document import Document
from src.dossiers.domain.exceptions import (
    DocumentNotFoundException,
    DossierAccessDeniedException,
    DossierNotFoundException,
    InvalidDocumentStateException,
)
from src.dossiers.domain.ports.document_repository import DocumentRepository
from src.dossiers.domain.ports.dossier_repository import DossierRepository
from src.shared.domain.exceptions import DomainError


@dataclass(frozen=True)
class ConfirmDocumentUploadCommand:
    """Command DTO pour confirmer un téléversement S3 réussi."""

    dossier_id: UUID
    document_id: UUID
    user_id: UUID


class ConfirmDocumentUploadCommandHandler:
    """Handler basculant l'état du document vers UPLOADED."""

    def __init__(
        self,
        dossier_repository: DossierRepository,
        document_repository: DocumentRepository,
    ) -> None:
        self._dossier_repository = dossier_repository
        self._document_repository = document_repository

    async def handle(self, command: ConfirmDocumentUploadCommand) -> Document:
        # 1. Vérification d'existence du dossier
        dossier = await self._dossier_repository.get_by_id(command.dossier_id)
        if dossier is None:
            raise DossierNotFoundException(f"Dossier {command.dossier_id} introuvable.")

        # 2. Vérification d'appartenance du dossier
        if dossier.user_id != command.user_id:
            raise DossierAccessDeniedException(
                "Accès refusé : vous n'êtes pas propriétaire de ce dossier."
            )

        # 3. Récupération du document
        document = await self._document_repository.find_by_id(command.document_id)
        if document is None:
            raise DocumentNotFoundException(
                f"Document {command.document_id} introuvable."
            )

        # 4. Vérification du raccordement au dossier demandé
        if document.dossier_id != command.dossier_id:
            raise InvalidDocumentStateException(
                f"Le document {command.document_id} n'appartient pas au dossier {command.dossier_id}."
            )

        # 5. Transition vers l'état UPLOADED
        try:
            document.mark_as_uploaded()
        except DomainError as exc:
            raise InvalidDocumentStateException(str(exc)) from exc

        # 6. Persistence du statut mis à jour
        await self._document_repository.save(document)

        return document
