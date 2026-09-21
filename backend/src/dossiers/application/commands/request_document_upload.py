"""Cas d'usage de demande d'URL pré-signée pour l'upload d'un document."""

from dataclasses import dataclass
from uuid import UUID, uuid4

from src.dossiers.domain.entities.document import Document
from src.dossiers.domain.exceptions import (
    DossierAccessDeniedException,
    DossierNotFoundException,
)
from src.dossiers.domain.ports.document_repository import DocumentRepository
from src.dossiers.domain.ports.document_storage_port import DocumentStoragePort
from src.dossiers.domain.ports.dossier_repository import DossierRepository
from src.dossiers.domain.value_objects.document_type import DocumentType


@dataclass(frozen=True)
class RequestDocumentUploadCommand:
    """Command DTO pour initialiser l'upload d'un document."""

    dossier_id: UUID
    user_id: UUID
    document_type: DocumentType
    filename: str
    content_type: str
    size: int


@dataclass(frozen=True)
class RequestDocumentUploadResult:
    """DTO de retour après initialisation."""

    document: Document
    upload_url: str


class RequestDocumentUploadCommandHandler:
    """Handler exécutant le processus d'initialisation de téléversement."""

    def __init__(
        self,
        dossier_repository: DossierRepository,
        document_repository: DocumentRepository,
        storage_port: DocumentStoragePort,
    ) -> None:
        self._dossier_repository = dossier_repository
        self._document_repository = document_repository
        self._storage_port = storage_port

    async def handle(
        self, command: RequestDocumentUploadCommand
    ) -> RequestDocumentUploadResult:
        # 1. Vérification d'existence du dossier
        dossier = await self._dossier_repository.get_by_id(command.dossier_id)
        if dossier is None:
            raise DossierNotFoundException(f"Dossier {command.dossier_id} introuvable.")

        # 2. Vérification d'appartenance à l'utilisateur courant (Sécurité IDOR)
        if dossier.user_id != command.user_id:
            raise DossierAccessDeniedException(
                "Accès refusé : vous n'êtes pas propriétaire de ce dossier."
            )

        # 3. Génération d'une clé S3 unique
        file_ext = command.filename.split(".")[-1] if "." in command.filename else "bin"
        document_id = uuid4()
        s3_key = f"dossiers/{command.dossier_id}/{document_id}.{file_ext}"

        # 4. Création du Document au statut PENDING
        document = Document.create_pending(
            id=document_id,
            dossier_id=command.dossier_id,
            type=command.document_type,
            s3_key=s3_key,
            original_filename=command.filename,
            content_type=command.content_type,
            size=command.size,
        )

        # 5. Sauvegarde en base de données
        await self._document_repository.save(document)

        # 6. Génération de l'URL pré-signée S3
        upload_url = await self._storage_port.generate_upload_url(
            s3_key=s3_key,
            content_type=command.content_type,
            expires_in=300,
        )

        # 7. Retour du résultat
        return RequestDocumentUploadResult(
            document=document,
            upload_url=upload_url,
        )
