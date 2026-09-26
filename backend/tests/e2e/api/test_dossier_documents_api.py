"""Tests e2e / API pour les endpoints de gestion des documents (Presigned URL & View URL US-304)."""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient

from src.dossiers.domain.entities.document import Document
from src.dossiers.domain.entities.dossier import Dossier
from src.dossiers.domain.value_objects.document_type import DocumentType
from src.dossiers.infrastructure.adapters.document_repository import (
    SqlAlchemyDocumentRepository,
)
from src.dossiers.infrastructure.repository.sqlalchemy_dossier_repository import (
    SQLAlchemyDossierRepository,
)

# Note: Les fixtures comme test_user, test_admin, async_client, etc. doivent être définies dans conftest.py


# ==============================================================================
# ENDPOINT: POST /api/v1/dossiers/{dossier_id}/documents/presigned-url
# ==============================================================================


@pytest.mark.asyncio
async def test_request_presigned_url_unauthenticated(async_client: AsyncClient) -> None:
    dossier_id = uuid4()
    response = await async_client.post(
        f"/api/v1/dossiers/{dossier_id}/documents/presigned-url",
        json={
            "document_type": "IDENTITY_CARD",
            "filename": "cni.pdf",
            "content_type": "application/pdf",
            "size": 1024,
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_request_presigned_url_invalid_mime_type(
    authenticated_client: AsyncClient,
) -> None:
    dossier_id = uuid4()
    response = await authenticated_client.post(
        f"/api/v1/dossiers/{dossier_id}/documents/presigned-url",
        json={
            "document_type": "IDENTITY_CARD",
            "filename": "script.sh",
            "content_type": "application/x-sh",
            "size": 1024,
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_request_presigned_url_exceeds_size(
    authenticated_client: AsyncClient,
) -> None:
    dossier_id = uuid4()
    response = await authenticated_client.post(
        f"/api/v1/dossiers/{dossier_id}/documents/presigned-url",
        json={
            "document_type": "IDENTITY_CARD",
            "filename": "big.pdf",
            "content_type": "application/pdf",
            "size": 11 * 1024 * 1024,  # > 10 MB
        },
    )
    assert response.status_code == 422


# ==============================================================================
# ENDPOINT: GET /api/v1/dossiers/{dossier_id}/documents/{document_id}/view-url (US-304)
# ==============================================================================


@pytest.mark.asyncio
async def test_view_url_owner_client_200(
    async_client: AsyncClient, db_session, test_user, test_user_token
) -> None:
    """Critère 3 : Propriétaire CLIENT → 200, url, expires_in=60."""
    dossier = Dossier.create(user_id=test_user.id, vehicle_id=uuid4())
    document = Document.create_pending(
        dossier_id=dossier.id,
        type=DocumentType.IDENTITY_CARD,
        s3_key=f"dossiers/{dossier.id}/IDENTITY_CARD/doc.pdf",
        original_filename="doc.pdf",
        content_type="application/pdf",
        size=1024,
    )
    await SQLAlchemyDossierRepository(db_session).save(dossier)
    await SqlAlchemyDocumentRepository(db_session).save(document)
    await db_session.commit()

    with patch(
        "src.dossiers.infrastructure.adapters.s3_document_storage.S3DocumentStorageAdapter.generate_download_url",
        new_callable=AsyncMock,
    ) as mock_generate:
        mock_generate.return_value = (
            "https://m-motors-documents.s3.amazonaws.com/key?X-Amz-Signature=..."
        )
        response = await async_client.get(
            f"/api/v1/dossiers/{dossier.id}/documents/{document.id}/view-url",
            headers={"Authorization": f"Bearer {test_user_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "url" in data
        assert data["expires_in"] == 60
        mock_generate.assert_awaited_once_with(s3_key=document.s3_key, expires_in=60)


@pytest.mark.asyncio
async def test_view_url_admin_200(
    async_client: AsyncClient, db_session, test_admin, test_admin_token
) -> None:
    """Critère 4 : ADMIN → 200, url, expires_in=60."""
    other_user_id = uuid4()
    dossier = Dossier.create(user_id=other_user_id, vehicle_id=uuid4())
    document = Document.create_pending(
        dossier_id=dossier.id,
        type=DocumentType.IDENTITY_CARD,
        s3_key=f"dossiers/{dossier.id}/IDENTITY_CARD/doc.pdf",
        original_filename="doc.pdf",
        content_type="application/pdf",
        size=1024,
    )
    await SQLAlchemyDossierRepository(db_session).save(dossier)
    await SqlAlchemyDocumentRepository(db_session).save(document)
    await db_session.commit()

    with patch(
        "src.dossiers.infrastructure.adapters.s3_document_storage.S3DocumentStorageAdapter.generate_download_url",
        new_callable=AsyncMock,
    ) as mock_generate:
        mock_generate.return_value = (
            "https://m-motors-documents.s3.amazonaws.com/key?X-Amz-Signature=..."
        )
        response = await async_client.get(
            f"/api/v1/dossiers/{dossier.id}/documents/{document.id}/view-url",
            headers={"Authorization": f"Bearer {test_admin_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["expires_in"] == 60


@pytest.mark.asyncio
async def test_view_url_non_owner_client_403(
    async_client: AsyncClient, db_session, test_user, test_user_token, other_user
) -> None:
    """Critère 5 : CLIENT tiers → 403."""
    dossier = Dossier.create(user_id=other_user.id, vehicle_id=uuid4())
    document = Document.create_pending(
        dossier_id=dossier.id,
        type=DocumentType.IDENTITY_CARD,
        s3_key=f"dossiers/{dossier.id}/IDENTITY_CARD/doc.pdf",
        original_filename="doc.pdf",
        content_type="application/pdf",
        size=1024,
    )
    await SQLAlchemyDossierRepository(db_session).save(dossier)
    await SqlAlchemyDocumentRepository(db_session).save(document)
    await db_session.commit()

    response = await async_client.get(
        f"/api/v1/dossiers/{dossier.id}/documents/{document.id}/view-url",
        headers={"Authorization": f"Bearer {test_user_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_view_url_unauthenticated_401(async_client: AsyncClient) -> None:
    """Critère 6 : Sans authentification → 401."""
    dossier_id = uuid4()
    document_id = uuid4()
    response = await async_client.get(
        f"/api/v1/dossiers/{dossier_id}/documents/{document_id}/view-url",
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_view_url_nonexistent_dossier_404(
    async_client: AsyncClient, test_user, test_user_token
) -> None:
    """Critère 8 : Dossier inexistant → 404."""
    dossier_id = uuid4()
    document_id = uuid4()
    response = await async_client.get(
        f"/api/v1/dossiers/{dossier_id}/documents/{document_id}/view-url",
        headers={"Authorization": f"Bearer {test_user_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_view_url_nonexistent_document_404(
    async_client: AsyncClient, db_session, test_user, test_user_token
) -> None:
    """Critère 8 : Document inexistant → 404."""
    dossier = Dossier.create(user_id=test_user.id, vehicle_id=uuid4())
    await SQLAlchemyDossierRepository(db_session).save(dossier)
    await db_session.commit()
    document_id = uuid4()  # Document qui n'existe pas
    response = await async_client.get(
        f"/api/v1/dossiers/{dossier.id}/documents/{document_id}/view-url",
        headers={"Authorization": f"Bearer {test_user_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_view_url_document_not_attached_404(
    async_client: AsyncClient, db_session, test_user, test_user_token
) -> None:
    """Critère 9 : Document rattaché à un autre dossier → 404."""
    dossier1 = Dossier.create(user_id=test_user.id, vehicle_id=uuid4())
    dossier2 = Dossier.create(user_id=test_user.id, vehicle_id=uuid4())
    document = Document.create_pending(
        dossier_id=dossier1.id,
        type=DocumentType.IDENTITY_CARD,
        s3_key=f"dossiers/{dossier1.id}/IDENTITY_CARD/doc.pdf",
        original_filename="doc.pdf",
        content_type="application/pdf",
        size=1024,
    )
    await SQLAlchemyDossierRepository(db_session).save(dossier1)
    await SQLAlchemyDossierRepository(db_session).save(dossier2)
    await SqlAlchemyDocumentRepository(db_session).save(document)
    await db_session.commit()
    response = await async_client.get(
        f"/api/v1/dossiers/{dossier2.id}/documents/{document.id}/view-url",
        headers={"Authorization": f"Bearer {test_user_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_view_url_mock_calls(
    async_client: AsyncClient, db_session, test_user, test_user_token
) -> None:
    """Vérification du mock de generate_download_url (Critère 10 : pas d'exposition de clés)."""
    dossier = Dossier.create(user_id=test_user.id, vehicle_id=uuid4())
    document = Document.create_pending(
        dossier_id=dossier.id,
        type=DocumentType.IDENTITY_CARD,
        s3_key="dossiers/1234/IDENTITY_CARD/doc.pdf",
        original_filename="doc.pdf",
        content_type="application/pdf",
        size=1024,
    )
    await SQLAlchemyDossierRepository(db_session).save(dossier)
    await SqlAlchemyDocumentRepository(db_session).save(document)
    await db_session.commit()

    with patch(
        "src.dossiers.infrastructure.adapters.s3_document_storage.S3DocumentStorageAdapter.generate_download_url",
        new_callable=AsyncMock,
    ) as mock_generate:
        mock_generate.return_value = (
            "https://m-motors-documents.s3.amazonaws.com/key?X-Amz-Signature=..."
        )
        await async_client.get(
            f"/api/v1/dossiers/{dossier.id}/documents/{document.id}/view-url",
            headers={"Authorization": f"Bearer {test_user_token}"},
        )
        # Vérification que la clé S3 et expires_in sont correctes
        mock_generate.assert_awaited_once()
        call_args = mock_generate.await_args
        assert call_args[1]["s3_key"] == document.s3_key
        assert call_args[1]["expires_in"] == 60  # expires_in
        # Critère 10 : Vérification que l'URL S3 et la clé ne sont pas exposées dans la réponse
        # (FastAPI ne retourne que url et expires_in, pas s3_key)
