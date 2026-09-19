"""Port de dépôt pour la gestion de la persistance des documents."""

from typing import Protocol
from uuid import UUID

from src.dossiers.domain.entities.document import Document


class DocumentRepository(Protocol):
    """Contrat d'infrastructure définissant les opérations de persistance des documents."""

    async def save(self, document: Document) -> None:
        """Sauvegarde ou met à jour une entité document."""
        ...

    async def find_by_id(self, document_id: UUID) -> Document | None:
        """Récupère un document par son identifiant unique."""
        ...

    async def find_by_dossier(self, dossier_id: UUID) -> list[Document]:
        """Récupère tous les documents rattachés à un dossier, triés par date de création décroissante."""
        ...