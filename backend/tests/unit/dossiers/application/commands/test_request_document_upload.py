"""Tests unitaires de la commande request_document_upload."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.dossiers.application.commands.request_document_upload import (
    RequestDocumentUploadCommand,
    RequestDocumentUploadCommandHandler,
)
from src.dossiers.domain.exceptions import (
    DossierAccessDeniedException,
    DossierNotFoundException,
)
from src.dossiers.domain.value_objects.document_type import DocumentType


@pytest.mark.asyncio
async def test_request_document_upload_success() -> None:
    dossier_id = uuid4()
    user_id = uuid4()

    mock_dossier = MagicMock()
    mock_dossier.id = dossier_id
    mock_dossier.user_id = user_id

    dossier_repo = AsyncMock()
    dossier_repo.find_by_id.return_value = mock_dossier

    document_repo = AsyncMock()
    storage_port = AsyncMock()
    storage_port.generate_upload_url.return_value = "https://s3.amazonaws.com/presigned-url"

    handler = RequestDocumentUploadCommandHandler(
        dossier_repository=dossier_repo,
        document_repository=document_repo,
        storage_port=storage_port,
    )

    command = RequestDocumentUploadCommand(
        dossier_id=dossier_id,
        user_id=user_id,
        document_type=DocumentType.IDENTITY_CARD,
        filename="cni.pdf",
        content_type="application/pdf",
        size=2048,
    )

    result = await handler.handle(command)

    assert result.upload_url == "https://s3.amazonaws.com/presigned-url"
    assert result.document.dossier_id == dossier_id
    document_repo.save.assert_called_once()
    storage_port.generate_upload_url.assert_called_once()


@pytest.mark.asyncio
async def test_request_document_upload_dossier_not_found() -> None:
    dossier_repo = AsyncMock()
    dossier_repo.find_by_id.return_value = None

    handler = RequestDocumentUploadCommandHandler(
        dossier_repository=dossier_repo,
        document_repository=AsyncMock(),
        storage_port=AsyncMock(),
    )

    command = RequestDocumentUploadCommand(
        dossier_id=uuid4(),
        user_id=uuid4(),
        document_type=DocumentType.IDENTITY_CARD,
        filename="cni.pdf",
        content_type="application/pdf",
        size=2048,
    )

    with pytest.raises(DossierNotFoundException):
        await handler.handle(command)


@pytest.mark.asyncio
async def test_request_document_upload_access_denied() -> None:
    dossier_id = uuid4()
    mock_dossier = MagicMock()
    mock_dossier.id = dossier_id
    mock_dossier.user_id = uuid4()  # Utilisateur différent

    dossier_repo = AsyncMock()
    dossier_repo.find_by_id.return_value = mock_dossier

    handler = RequestDocumentUploadCommandHandler(
        dossier_repository=dossier_repo,
        document_repository=AsyncMock(),
        storage_port=AsyncMock(),
    )

    command = RequestDocumentUploadCommand(
        dossier_id=dossier_id,
        user_id=uuid4(),  # Utilisateur non propriétaire
        document_type=DocumentType.IDENTITY_CARD,
        filename="cni.pdf",
        content_type="application/pdf",
        size=2048,
    )

    with pytest.raises(DossierAccessDeniedException):
        await handler.handle(command)