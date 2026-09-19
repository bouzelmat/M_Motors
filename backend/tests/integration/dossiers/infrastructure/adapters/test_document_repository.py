"""Tests d'intégration pour SqlAlchemyDocumentRepository."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.dossiers.domain.entities.document import Document
from src.dossiers.domain.value_objects.document_status import DocumentStatus
from src.dossiers.domain.value_objects.document_type import DocumentType
from src.dossiers.domain.value_objects.dossier_status import DossierStatus
from src.dossiers.infrastructure.models.dossier_model import DossierModel
from src.dossiers.infrastructure.adapters.document_repository import (
    SqlAlchemyDocumentRepository,
)


@pytest.mark.asyncio
async def test_repository_save_and_find_by_id(db_session: AsyncSession) -> None:
    repo = SqlAlchemyDocumentRepository(db_session)
    dossier_id = uuid4()
    
    # Création du dossier englobant
    dossier = DossierModel(
        id=dossier_id,
        user_id=uuid4(),
        vehicle_id=uuid4(),
        status=DossierStatus.DRAFT,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(dossier)
    await db_session.flush()

    doc = Document.create_pending(
        dossier_id=dossier_id,
        type=DocumentType.IDENTITY_CARD,
        s3_key="dossiers/1/cni.pdf",
        original_filename="cni.pdf",
        content_type="application/pdf",
        size=1024,
    )

    await repo.save(doc)
    await db_session.commit()

    retrieved = await repo.find_by_id(doc.id)
    assert retrieved is not None
    assert retrieved.id == doc.id
    assert retrieved.s3_key == "dossiers/1/cni.pdf"


@pytest.mark.asyncio
async def test_repository_find_by_id_returns_none_when_missing(
    db_session: AsyncSession,
) -> None:
    repo = SqlAlchemyDocumentRepository(db_session)
    retrieved = await repo.find_by_id(uuid4())
    assert retrieved is None


@pytest.mark.asyncio
async def test_repository_find_by_dossier_ordered_by_created_at_desc(
    db_session: AsyncSession,
) -> None:
    repo = SqlAlchemyDocumentRepository(db_session)
    dossier_id = uuid4()

    dossier = DossierModel(
        id=dossier_id,
        user_id=uuid4(),
        vehicle_id=uuid4(),
        status=DossierStatus.DRAFT,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(dossier)
    await db_session.flush()

    now = datetime.now(timezone.utc)
    doc_older = Document.create_pending(
        dossier_id=dossier_id,
        type=DocumentType.IDENTITY_CARD,
        s3_key="dossiers/1/old.pdf",
        original_filename="old.pdf",
        content_type="application/pdf",
        size=1024,
        now=now - timedelta(hours=2),
    )
    doc_newer = Document.create_pending(
        dossier_id=dossier_id,
        type=DocumentType.PAYSLIP,
        s3_key="dossiers/1/new.pdf",
        original_filename="new.pdf",
        content_type="application/pdf",
        size=2048,
        now=now,
    )

    await repo.save(doc_older)
    await repo.save(doc_newer)
    await db_session.commit()

    docs = await repo.find_by_dossier(dossier_id)
    assert len(docs) == 2
    assert docs[0].id == doc_newer.id
    assert docs[1].id == doc_older.id