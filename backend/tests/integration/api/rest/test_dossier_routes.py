"""Tests d'intégration HTTP pour les routes FastAPI /api/v1/dossiers."""

from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient
from starlette import status
from src.dossiers.domain.value_objects.document_status import DocumentStatus
from src.dossiers.domain.value_objects.dossier_status import DossierStatus
from src.dossiers.domain.value_objects.document_type import DocumentType
from src.dossiers.infrastructure.models.document_model import DocumentModel
from src.dossiers.infrastructure.models.dossier_model import DossierModel


@pytest.mark.asyncio
async def test_create_dossier_unauthorized(client: AsyncClient) -> None:
    csrf_response = await client.get("/api/v1/auth/csrf")
    csrf_headers = {"X-CSRF-Token": csrf_response.json()["csrf_token"]}
    response = await client.post(
        "/api/v1/dossiers",
        json={"vehicle_id": str(uuid4())},
        headers=csrf_headers,
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_create_dossier_invalid_payload(
    authenticated_client: AsyncClient,
) -> None:
    csrf_response = await authenticated_client.get("/api/v1/auth/csrf")
    csrf_headers = {"X-CSRF-Token": csrf_response.json()["csrf_token"]}
    # Kilométrage négatif invalide
    payload = {
        "vehicle_id": str(uuid4()),
        "trade_in": {
            "registration": "AB-123-CD",
            "mileage": -500,
        },
    }
    response = await authenticated_client.post(
        "/api/v1/dossiers",
        json=payload,
        headers=csrf_headers,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_create_dossier_success(
    authenticated_client: AsyncClient,
    existing_available_vehicle_id: str,
) -> None:
    csrf_response = await authenticated_client.get("/api/v1/auth/csrf")
    csrf_headers = {"X-CSRF-Token": csrf_response.json()["csrf_token"]}
    payload = {
        "vehicle_id": existing_available_vehicle_id,
        "trade_in": {
            "registration": "AA-888-ZZ",
            "mileage": 15000,
        },
        "financing_plan": {
            "down_payment": "2000.00",
            "duration_months": 24,
            "monthly_payment": "150.00",
        },
    }

    response = await authenticated_client.post(
        "/api/v1/dossiers",
        json=payload,
        headers=csrf_headers,
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "id" in data
    assert data["vehicle_id"] == existing_available_vehicle_id
    assert data["status"] == "DRAFT"


@pytest.mark.asyncio
async def test_list_user_dossiers_includes_requested_document_types(
    authenticated_client: AsyncClient,
    existing_available_vehicle_id: str,
    db_session,
) -> None:
    csrf_response = await authenticated_client.get("/api/v1/auth/csrf")
    csrf_headers = {"X-CSRF-Token": csrf_response.json()["csrf_token"]}
    create_response = await authenticated_client.post(
        "/api/v1/dossiers",
        json={"vehicle_id": existing_available_vehicle_id},
        headers=csrf_headers,
    )
    dossier_id = UUID(create_response.json()["id"])

    dossier = await db_session.get(DossierModel, dossier_id)
    assert dossier is not None
    dossier.status = DossierStatus.DOCUMENTS_PENDING
    dossier.requested_document_types = ["IDENTITY_CARD", "PAYSLIP"]
    await db_session.flush()

    response = await authenticated_client.get("/api/v1/dossiers/me")

    assert response.status_code == status.HTTP_200_OK
    dossier_data = next(
        item for item in response.json() if item["id"] == str(dossier_id)
    )
    assert dossier_data["status"] == "DOCUMENTS_PENDING"
    assert dossier_data["requested_document_types"] == ["IDENTITY_CARD", "PAYSLIP"]


@pytest.mark.asyncio
async def test_submit_dossier_success(
    authenticated_client: AsyncClient,
    existing_available_vehicle_id: str,
    db_session,
) -> None:
    csrf_response = await authenticated_client.get("/api/v1/auth/csrf")
    csrf_headers = {"X-CSRF-Token": csrf_response.json()["csrf_token"]}
    create_response = await authenticated_client.post(
        "/api/v1/dossiers",
        json={
            "vehicle_id": existing_available_vehicle_id,
            "financing_plan": {
                "down_payment": "2000.00",
                "duration_months": 24,
                "monthly_payment": "150.00",
            },
        },
        headers=csrf_headers,
    )
    dossier_id = create_response.json()["id"]
    db_session.add(
        DocumentModel(
            id=uuid4(),
            dossier_id=UUID(dossier_id),
            type=DocumentType.IDENTITY_CARD,
            s3_key="test/identity.pdf",
            status=DocumentStatus.UPLOADED,
            original_filename="identity.pdf",
            content_type="application/pdf",
            size=100,
        )
    )
    await db_session.flush()

    response = await authenticated_client.post(
        f"/api/v1/dossiers/{dossier_id}/submit",
        headers=csrf_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == dossier_id
    assert response.json()["status"] == "SUBMITTED"


@pytest.mark.asyncio
async def test_submit_dossier_without_uploaded_document_returns_conflict(
    authenticated_client: AsyncClient,
    existing_available_vehicle_id: str,
) -> None:
    csrf_response = await authenticated_client.get("/api/v1/auth/csrf")
    csrf_headers = {"X-CSRF-Token": csrf_response.json()["csrf_token"]}
    create_response = await authenticated_client.post(
        "/api/v1/dossiers",
        json={"vehicle_id": existing_available_vehicle_id},
        headers=csrf_headers,
    )
    dossier_id = create_response.json()["id"]

    response = await authenticated_client.post(
        f"/api/v1/dossiers/{dossier_id}/submit",
        headers=csrf_headers,
    )

    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_cancel_draft_releases_vehicle_for_another_dossier(
    authenticated_client: AsyncClient,
    existing_available_vehicle_id: str,
) -> None:
    csrf_response = await authenticated_client.get("/api/v1/auth/csrf")
    csrf_headers = {"X-CSRF-Token": csrf_response.json()["csrf_token"]}
    create_response = await authenticated_client.post(
        "/api/v1/dossiers",
        json={
            "vehicle_id": existing_available_vehicle_id,
            "financing_plan": {
                "down_payment": "2000.00",
                "duration_months": 24,
                "monthly_payment": "150.00",
            },
        },
        headers=csrf_headers,
    )
    dossier_id = create_response.json()["id"]

    cancel_response = await authenticated_client.post(
        f"/api/v1/dossiers/{dossier_id}/cancel",
        headers=csrf_headers,
    )

    assert cancel_response.status_code == status.HTTP_200_OK
    assert cancel_response.json()["status"] == "CANCELLED"

    retry_response = await authenticated_client.post(
        "/api/v1/dossiers",
        json={"vehicle_id": existing_available_vehicle_id},
        headers=csrf_headers,
    )
    assert retry_response.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_confirm_upload_returns_document_id(
    authenticated_client: AsyncClient,
    existing_available_vehicle_id: str,
    db_session,
) -> None:
    csrf_response = await authenticated_client.get("/api/v1/auth/csrf")
    csrf_headers = {"X-CSRF-Token": csrf_response.json()["csrf_token"]}
    create_response = await authenticated_client.post(
        "/api/v1/dossiers",
        json={"vehicle_id": existing_available_vehicle_id},
        headers=csrf_headers,
    )
    dossier_id = create_response.json()["id"]
    document_id = uuid4()
    db_session.add(
        DocumentModel(
            id=document_id,
            dossier_id=UUID(dossier_id),
            type=DocumentType.IDENTITY_CARD,
            s3_key=f"dossiers/{dossier_id}/{document_id}.pdf",
            status=DocumentStatus.PENDING,
            original_filename="identity.pdf",
            content_type="application/pdf",
            size=100,
        )
    )
    await db_session.flush()

    response = await authenticated_client.post(
        f"/api/v1/dossiers/{dossier_id}/documents/{document_id}/confirm",
        headers=csrf_headers,
    )

    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json()["document_id"] == str(document_id)
    assert response.json()["status"] == "UPLOADED"
    assert response.json()["uploaded_at"] is not None


@pytest.mark.asyncio
async def test_submit_dossier_unauthorized(client: AsyncClient) -> None:
    csrf_response = await client.get("/api/v1/auth/csrf")
    csrf_headers = {"X-CSRF-Token": csrf_response.json()["csrf_token"]}
    response = await client.post(
        f"/api/v1/dossiers/{uuid4()}/submit",
        headers=csrf_headers,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
