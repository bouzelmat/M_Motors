"""Tests e2e / API pour les endpoints de gestion des documents."""

from uuid import uuid4

import pytest
from httpx import AsyncClient


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