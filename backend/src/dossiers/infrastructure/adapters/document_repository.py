"""Implémentation SQLAlchemy 2.x du dépôt de documents."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dossiers.domain.entities.document import Document
from src.dossiers.domain.ports.document_repository import DocumentRepository
from src.dossiers.infrastructure.models.document_model import DocumentModel
from src.dossiers.infrastructure.mapper.document_mapper import DocumentMapper


class SqlAlchemyDocumentRepository(DocumentRepository):
    """Adaptateur de dépôt persistant les documents via SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, document: Document) -> None:
        """Sauvegarde l'entité Document en effectuant un merge du modèle ORM."""
        model = DocumentMapper.to_model(document)
        await self._session.merge(model)

    async def find_by_id(self, document_id: UUID) -> Document | None:
        """Recherche un document par ID et retourne l'entité domaine ou None."""
        stmt = select(DocumentModel).where(DocumentModel.id == document_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return DocumentMapper.to_domain(model)

    async def find_by_dossier(self, dossier_id: UUID) -> list[Document]:
        """Récupère la liste des documents d'un dossier triée par created_at desc."""
        stmt = (
            select(DocumentModel)
            .where(DocumentModel.dossier_id == dossier_id)
            .order_by(DocumentModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [DocumentMapper.to_domain(model) for model in models]