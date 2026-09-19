"""Entité métier Document représentant une pièce justificative."""

from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Optional
from uuid import UUID, uuid4

from src.dossiers.domain.value_objects.document_status import DocumentStatus
from src.dossiers.domain.value_objects.document_type import DocumentType
from src.shared.domain.exceptions import DomainError


@dataclass
class Document:
    """Entité métier représentant un document justificatif rattaché à un dossier."""

    id: UUID
    dossier_id: UUID
    type: DocumentType
    s3_key: str
    status: DocumentStatus
    original_filename: str
    content_type: str
    size: int
    created_at: datetime
    uploaded_at: Optional[datetime] = None

    @classmethod
    def create_pending(
        cls,
        dossier_id: UUID,
        type: DocumentType,
        s3_key: str,
        original_filename: str,
        content_type: str,
        size: int,
        document_id: Optional[UUID] = None,
        now: Optional[datetime] = None,
    ) -> "Document":
        """Instancie un document au statut PENDING."""
        current_time = now or datetime.now(timezone.utc)
        return cls(
            id=document_id or uuid4(),
            dossier_id=dossier_id,
            type=type,
            s3_key=s3_key,
            status=DocumentStatus.PENDING,
            original_filename=original_filename,
            content_type=content_type,
            size=size,
            created_at=current_time,
            uploaded_at=None,
        )

    def mark_as_uploaded(self, now: Optional[datetime] = None) -> None:
        """Passe le statut du document à UPLOADED.
        
        La transition n'est autorisée que depuis le statut PENDING.
        """
        if self.status != DocumentStatus.PENDING:
            raise DomainError(
                f"Impossible de marquer comme téléversé un document au statut '{self.status.value}'."
            )
        
        self.status = DocumentStatus.UPLOADED
        self.uploaded_at = now or datetime.now(timezone.utc)
