"""Command et Command Handler pour l'ajout d'un document à un dossier."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import BinaryIO
from uuid import UUID

from src.dossiers.domain.entities.dossier import Dossier
from src.dossiers.domain.ports.document_storage_ports import DocumentStoragePort
from src.dossiers.domain.ports.dossier_repository import DossierRepository
from src.dossiers.domain.value_objects.dossier_status import DossierStatus
from src.shared.domain.exceptions import DomainError
from src.shared.domain.ports.unit_of_work import AbstractUnitOfWork


@dataclass(frozen=True)
class UploadDocumentCommand:
    """Commande transportant les données nécessaires au versement d'une pièce justificative."""

    dossier_id: UUID
    user_id: UUID
    document_type: str
    file_content: BinaryIO
    file_name: str


class UploadDocumentCommandHandler:
    """Orchestrateur de dépôt de document garantissant l'initialisation du temporiseur d'expiration."""

    def __init__(
        self,
        dossier_repository: DossierRepository,
        document_storage: DocumentStoragePort,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._dossier_repository = dossier_repository
        self._document_storage = document_storage
        self._uow = uow

    async def handle(self, command: UploadDocumentCommand) -> Dossier:
        """Ajoute un document au dossier et enclenche l'horodatage upload_started_at si premier dépôt."""
        dossier = await self._dossier_repository.get_by_id(command.dossier_id)

        if dossier is None:
            raise DomainError(f"Dossier introuvable : {command.dossier_id}")

        if dossier.user_id != command.user_id:
            raise DomainError("Vous n'êtes pas autorisé à modifier ce dossier.")

        if dossier.status != DossierStatus.DRAFT:
            raise DomainError(
                f"Impossible d'ajouter un document à un dossier au statut {dossier.status.value}."
            )

        now = datetime.now(timezone.utc)

        # Enregistrement du fichier via le port d'infrastructure (S3, stockage local, etc.)
        await self._document_storage.upload(
            dossier_id=command.dossier_id,
            document_type=command.document_type,
            file_name=command.file_name,
            content=command.file_content,
        )

        # Horodatage idempotence : déclenché uniquement lors du premier upload
        updated_dossier = dossier.mark_upload_started(now=now)

        async with self._uow:
            await self._dossier_repository.save(updated_dossier)
            await self._uow.commit()

        return updated_dossier
