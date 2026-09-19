"""Tests unitaires de la commande confirm_document_upload."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.dossiers.application.commands.confirm_document_upload import (
    ConfirmDocumentUploadCommand,
    ConfirmDocumentUploadCommandHandler,
)
from src.dossiers.domain.entities.document import Document
from src.dossiers.domain.exceptions import (
    DocumentNotFoundException,
    DossierAccessDeniedException,
    DossierNotFoundException,
    InvalidDocumentStateException,
)
from src.dossiers.domain.value_objects.document_status import DocumentStatus
from src.dossiers.domain.value_objects.document_type import DocumentType


@pytest.mark.asyncio
async def test_confirm_document_upload_success() -> None:
    dossier_id = uuid4()
    user_id = uuid4()
    doc_id = uuid4()

    mock_dossier = MagicMock(id=dossier_id, user_id=user_id)
    doc = Document.create_pending(
        id=doc_id,
        dossier_id=dossier_id,
        type=DocumentType.IDENTITY_CARD,
        s3_key="key",
        original_filename="cni.pdf",
        content_type="application/pdf",
        size=1000,
    )

    dossier_repo = AsyncMock()
    dossier_repo.find_by_id.return_value = mock_dossier

    doc_repo = AsyncMock()
    doc_repo.find_by_id.return_value = doc

    handler = ConfirmDocumentUploadCommandHandler(dossier_repo, doc_repo)
    updated = await handler.handle(
        ConfirmDocumentUploadCommand(dossier_id, doc_id, user_id)
    )

    assert updated.status == DocumentStatus.UPLOADED
    assert updated.uploaded_at is not None
    doc_repo.save.assert_called_once_with(doc)


@pytest.mark.asyncio
async def test_confirm_document_already_uploaded_raises_exception() -> None:
    dossier_id = uuid4()
    user_id = uuid4()
    doc_id = uuid4()

    mock_dossier = MagicMock(id=dossier_id, user_id=user_id)
    doc = Document.create_pending(
        id=doc_id,
        dossier_id=dossier_id,
        type=DocumentType.IDENTITY_CARD,
        s3_key="key",
        original_filename="cni.pdf",
        content_type="application/pdf",
        size=1000,
    )
    doc.mark_as_uploaded()  # Déjà uploadé

    dossier_repo = AsyncMock(find_by_id=AsyncMock(return_value=mock_dossier))
    doc_repo = AsyncMock(find_by_id=AsyncMock(return_value=doc))

    handler = ConfirmDocumentUploadCommandHandler(dossier_repo, doc_repo)

    with pytest.raises(InvalidDocumentStateException):
        await handler.handle(ConfirmDocumentUploadCommand(dossier_id, doc_id, user_id))