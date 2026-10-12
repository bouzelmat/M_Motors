"""Integration test for DocumentModel persistence."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dossiers.domain.value_objects.document_status import DocumentStatus
from src.dossiers.domain.value_objects.document_type import DocumentType
from src.dossiers.domain.value_objects.dossier_status import DossierStatus
from src.dossiers.infrastructure.orm.document_model import DocumentModel
from src.dossiers.infrastructure.orm.dossier_model import DossierModel


@pytest.mark.asyncio
async def test_insert_and_read_document_model(db_session: AsyncSession) -> None:
    # 1. Dossier parent
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

    # 2. Insertion du document avec le type mis à jour
    doc_id = uuid4()
    created_at = datetime.now(timezone.utc)
    document = DocumentModel(
        id=doc_id,
        dossier_id=dossier_id,
        type=DocumentType.IDENTITY_CARD,
        s3_key="dossiers/test/cni.pdf",
        status=DocumentStatus.PENDING,
        original_filename="cni_identity.pdf",
        content_type="application/pdf",
        size=2048,
        created_at=created_at,
        uploaded_at=None,
    )
    db_session.add(document)
    await db_session.commit()

    # 3. Relecture
    stmt = select(DocumentModel).where(DocumentModel.id == doc_id)
    result = await db_session.execute(stmt)
    retrieved_doc = result.scalar_one_or_none()

    assert retrieved_doc is not None
    assert retrieved_doc.id == doc_id
    assert retrieved_doc.type == DocumentType.IDENTITY_CARD
    assert retrieved_doc.status == DocumentStatus.PENDING
