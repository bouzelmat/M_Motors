"""Port secondaire pour le stockage physique des pièces justificatives."""

from typing import BinaryIO, Protocol
from uuid import UUID


class DocumentStoragePort(Protocol):
    """Contrat d'infrastructure définissant les opérations de gestion de fichiers."""

    async def upload(
        self,
        dossier_id: UUID,
        document_type: str,
        file_name: str,
        content: BinaryIO,
    ) -> str:
        """Stocke le contenu binaire d'une pièce justificative et retourne son URI/emplacement."""
        ...
