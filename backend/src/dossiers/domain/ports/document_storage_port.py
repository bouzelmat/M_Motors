"""Port secondaire pour le stockage physique des pièces justificatives."""

from typing import BinaryIO, Protocol
from uuid import UUID


class DocumentStoragePort(Protocol):
    """Contrat d'infrastructure définissant les opérations de stockage."""

    async def upload(
        self,
        dossier_id: UUID,
        document_type: str,
        file_name: str,
        content: BinaryIO,
    ) -> str:
        """Stocke le contenu binaire d'une pièce justificative et retourne son URI/emplacement."""
        ...

    async def generate_upload_url(
        self,
        s3_key: str,
        content_type: str,
        expires_in: int = 300,
    ) -> str:
        """Génère une URL pré-signée S3 pour le téléversement direct d'une pièce justificative."""
        ...

    async def generate_download_url(
        self,
        s3_key: str,
        expires_in: int = 60,
    ) -> str:
        """Génère une URL pré-signée GET pour consulter un document (US-304 - Critère 7)."""
        ...
