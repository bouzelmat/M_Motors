"""Mapper de persistance entre l'entité de domaine Document et DocumentModel."""

from src.dossiers.domain.entities.document import Document
from src.dossiers.infrastructure.orm.document_model import DocumentModel


class DocumentMapper:
    """Convertit les entités Document en modèles ORM et inversement."""

    @staticmethod
    def to_domain(model: DocumentModel) -> Document:
        """Convertit un modèle ORM DocumentModel en entité de domaine Document.

        Conserve la valeur None pour uploaded_at si le document est PENDING.
        """
        return Document(
            id=model.id,
            dossier_id=model.dossier_id,
            type=model.type,
            s3_key=model.s3_key,
            status=model.status,
            original_filename=model.original_filename,
            content_type=model.content_type,
            size=model.size,
            created_at=model.created_at,
            uploaded_at=model.uploaded_at,
        )

    @staticmethod
    def to_model(entity: Document) -> DocumentModel:
        """Convertit une entité de domaine Document en modèle ORM DocumentModel."""
        return DocumentModel(
            id=entity.id,
            dossier_id=entity.dossier_id,
            type=entity.type,
            s3_key=entity.s3_key,
            status=entity.status,
            original_filename=entity.original_filename,
            content_type=entity.content_type,
            size=entity.size,
            created_at=entity.created_at,
            uploaded_at=entity.uploaded_at,
        )
