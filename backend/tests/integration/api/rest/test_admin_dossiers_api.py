"""Tests d'intégration pour les routes d'administration des dossiers."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.infrastructure.orm.user_model import UserModel
from src.dossiers.domain.entities.dossier import Dossier
from src.dossiers.domain.value_objects.dossier_status import DossierStatus
from src.dossiers.domain.value_objects.financing_plan import FinancingPlan
from src.dossiers.domain.value_objects.trade_in import TradeIn
from src.dossiers.infrastructure.repository.sqlalchemy_dossier_repository import (
    SQLAlchemyDossierRepository,
)
from src.vehicles.infrastructure.orm.vehicle_model import VehicleModel

# Imports pour les types Enum non-nullables du modèle VehicleModel
from src.vehicles.domain.value_objects.energy_type import EnergyType
from src.vehicles.domain.value_objects.vehicle_status import VehicleStatus
from src.vehicles.domain.value_objects.catalog_type import CatalogType


async def create_test_user(
    session: AsyncSession, email: str = "client.dossier@example.com"
) -> UserModel:
    user = UserModel(
        id=uuid4(),
        email=email,
        hashed_password="fake_hashed_password",
        first_name="John",
        last_name="Doe",
        role="CLIENT",
        is_active=True,
    )
    session.add(user)
    await session.flush()
    return user


async def create_test_vehicle(
    session: AsyncSession, brand: str = "Renault", model: str = "Clio"
) -> VehicleModel:
    vehicle = VehicleModel(
        id=uuid4(),
        brand=brand,
        model=model,
        year=2020,
        mileage=50000,
        energy_type=EnergyType.ESSENCE,
        catalog_type=CatalogType.RENTAL,
        status=VehicleStatus.AVAILABLE,
        monthly_rent=300,
    )
    session.add(vehicle)
    await session.flush()
    return vehicle


# === TESTS EXISTANTS (US-502) ===


@pytest.mark.asyncio
async def test_get_pending_dossiers_forbidden_for_non_admin(
    async_client: AsyncClient,
    test_user_token: str,
) -> None:
    response = await async_client.get(
        "/api/v1/admin/dossiers/pending",
        headers={"Authorization": f"Bearer {test_user_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_pending_dossiers_success(
    async_client: AsyncClient,
    test_admin_token: str,
    db_session: AsyncSession,
) -> None:
    repository = SQLAlchemyDossierRepository(db_session)
    now = datetime.now(timezone.utc)
    user = await create_test_user(db_session, email="client.dossier@example.com")
    vehicle = await create_test_vehicle(db_session, brand="Renault", model="Clio")
    dossier = Dossier.create(user_id=user.id, vehicle_id=vehicle.id).submit(
        now=now - timedelta(minutes=30)
    )
    await repository.save(dossier)
    await db_session.commit()

    response = await async_client.get(
        "/api/v1/admin/dossiers/pending",
        headers={"Authorization": f"Bearer {test_admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    item = next(d for d in data if d["id"] == str(dossier.id))
    assert item["client_email"] == "client.dossier@example.com"
    assert item["vehicle_brand"] == "Renault"
    assert item["vehicle_model"] == "Clio"
    assert item["status"] == DossierStatus.SUBMITTED.value
    assert item["submitted_at"] is not None


@pytest.mark.asyncio
async def test_validate_dossier_by_admin(
    async_client: AsyncClient,
    test_admin_token: str,
    db_session: AsyncSession,
) -> None:
    repository = SQLAlchemyDossierRepository(db_session)
    user = await create_test_user(db_session, email="validate@example.com")
    vehicle = await create_test_vehicle(db_session)
    dossier = Dossier.create(user_id=user.id, vehicle_id=vehicle.id).submit()
    await repository.save(dossier)
    await db_session.commit()

    response = await async_client.post(
        f"/api/v1/admin/dossiers/{dossier.id}/validate",
        json={"comment": "Dossier complet et conforme."},
        headers={"Authorization": f"Bearer {test_admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == DossierStatus.VALIDATED.value

    updated = await repository.get_by_id(dossier.id)
    assert updated is not None
    assert updated.status == DossierStatus.VALIDATED
    assert updated.comment == "Dossier complet et conforme."


@pytest.mark.asyncio
async def test_reject_dossier_by_admin(
    async_client: AsyncClient,
    test_admin_token: str,
    db_session: AsyncSession,
) -> None:
    repository = SQLAlchemyDossierRepository(db_session)
    user = await create_test_user(db_session, email="reject@example.com")
    vehicle = await create_test_vehicle(db_session)
    dossier = Dossier.create(user_id=user.id, vehicle_id=vehicle.id).submit()
    await repository.save(dossier)
    await db_session.commit()

    response = await async_client.post(
        f"/api/v1/admin/dossiers/{dossier.id}/reject",
        json={"reason": "Documents illisibles, veuillez renvoyer."},
        headers={"Authorization": f"Bearer {test_admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == DossierStatus.REJECTED.value

    updated = await repository.get_by_id(dossier.id)
    assert updated is not None
    assert updated.status == DossierStatus.REJECTED
    assert updated.rejection_reason == "Documents illisibles, veuillez renvoyer."
    assert updated.rejected_at is not None


@pytest.mark.asyncio
async def test_request_documents_by_admin(
    async_client: AsyncClient,
    test_admin_token: str,
    db_session: AsyncSession,
) -> None:
    repository = SQLAlchemyDossierRepository(db_session)
    user = await create_test_user(db_session, email="docs@example.com")
    vehicle = await create_test_vehicle(db_session)
    dossier = Dossier.create(user_id=user.id, vehicle_id=vehicle.id).submit()
    await repository.save(dossier)
    await db_session.commit()

    response = await async_client.post(
        f"/api/v1/admin/dossiers/{dossier.id}/request-documents",
        json={"document_types": ["IDENTITY_CARD", "PAYSLIP"]},
        headers={"Authorization": f"Bearer {test_admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == DossierStatus.DOCUMENTS_PENDING.value

    updated = await repository.get_by_id(dossier.id)
    assert updated is not None
    assert updated.status == DossierStatus.DOCUMENTS_PENDING
    assert updated.requested_document_types == ["IDENTITY_CARD", "PAYSLIP"]


@pytest.mark.asyncio
async def test_invalid_transition_returns_409(
    async_client: AsyncClient,
    test_admin_token: str,
    db_session: AsyncSession,
) -> None:
    repository = SQLAlchemyDossierRepository(db_session)
    user = await create_test_user(db_session, email="draft@example.com")
    vehicle = await create_test_vehicle(db_session)
    dossier = Dossier.create(user_id=user.id, vehicle_id=vehicle.id)  # DRAFT
    await repository.save(dossier)
    await db_session.commit()

    response = await async_client.post(
        f"/api/v1/admin/dossiers/{dossier.id}/validate",
        json={},
        headers={"Authorization": f"Bearer {test_admin_token}"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_nonexistent_dossier_returns_404(
    async_client: AsyncClient,
    test_admin_token: str,
) -> None:
    fake_id = uuid4()
    response = await async_client.post(
        f"/api/v1/admin/dossiers/{fake_id}/validate",
        json={},
        headers={"Authorization": f"Bearer {test_admin_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_client_role_forbidden_on_validate(
    async_client: AsyncClient,
    test_user_token: str,
    db_session: AsyncSession,
) -> None:
    repository = SQLAlchemyDossierRepository(db_session)
    user = await create_test_user(db_session, email="client403@example.com")
    vehicle = await create_test_vehicle(db_session)
    dossier = Dossier.create(user_id=user.id, vehicle_id=vehicle.id).submit()
    await repository.save(dossier)
    await db_session.commit()

    response = await async_client.post(
        f"/api/v1/admin/dossiers/{dossier.id}/validate",
        json={},
        headers={"Authorization": f"Bearer {test_user_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_no_token_returns_401(
    async_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    repository = SQLAlchemyDossierRepository(db_session)
    user = await create_test_user(db_session, email="noauth@example.com")
    vehicle = await create_test_vehicle(db_session)
    dossier = Dossier.create(user_id=user.id, vehicle_id=vehicle.id).submit()
    await repository.save(dossier)
    await db_session.commit()

    response = await async_client.post(
        f"/api/v1/admin/dossiers/{dossier.id}/validate",
        json={},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_unknown_document_type_returns_422(
    async_client: AsyncClient,
    test_admin_token: str,
    db_session: AsyncSession,
) -> None:
    repository = SQLAlchemyDossierRepository(db_session)
    user = await create_test_user(db_session, email="unknowndoc@example.com")
    vehicle = await create_test_vehicle(db_session)
    dossier = Dossier.create(user_id=user.id, vehicle_id=vehicle.id).submit()
    await repository.save(dossier)
    await db_session.commit()

    response = await async_client.post(
        f"/api/v1/admin/dossiers/{dossier.id}/request-documents",
        json={"document_types": ["UNKNOWN_TYPE"]},
        headers={"Authorization": f"Bearer {test_admin_token}"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_reject_with_short_reason_returns_422(
    async_client: AsyncClient,
    test_admin_token: str,
    db_session: AsyncSession,
) -> None:
    repository = SQLAlchemyDossierRepository(db_session)
    user = await create_test_user(db_session, email="shortreason@example.com")
    vehicle = await create_test_vehicle(db_session)
    dossier = Dossier.create(user_id=user.id, vehicle_id=vehicle.id).submit()
    await repository.save(dossier)
    await db_session.commit()

    response = await async_client.post(
        f"/api/v1/admin/dossiers/{dossier.id}/reject",
        json={"reason": "Court"},  # 5 caractères (déclenche le 422)
        headers={"Authorization": f"Bearer {test_admin_token}"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_dossier_detail_success(
    async_client: AsyncClient,
    test_admin_token: str,
    db_session: AsyncSession,
) -> None:
    repository = SQLAlchemyDossierRepository(db_session)
    user = await create_test_user(db_session, email="detail@example.com")
    vehicle = await create_test_vehicle(db_session)
    dossier = Dossier.create(user_id=user.id, vehicle_id=vehicle.id).submit()
    await repository.save(dossier)
    await db_session.commit()

    response = await async_client.get(
        f"/api/v1/admin/dossiers/{dossier.id}",
        headers={"Authorization": f"Bearer {test_admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(dossier.id)
    assert data["status"] == DossierStatus.SUBMITTED.value


# === NOUVEAUX TESTS US-503 ===


@pytest.mark.asyncio
async def test_get_dossier_detail_with_financing_and_trade_in(
    async_client: AsyncClient,
    test_admin_token: str,
    db_session: AsyncSession,
) -> None:
    """Teste le détail d'un dossier avec financement et reprise."""
    repository = SQLAlchemyDossierRepository(db_session)
    user = await create_test_user(db_session, email="financing@example.com")
    vehicle = await create_test_vehicle(db_session, brand="Peugeot", model="208")

    financing_plan = FinancingPlan(
        down_payment=Decimal("2000.00"),
        duration_months=48,
        monthly_payment=Decimal("395.50"),
    )
    trade_in = TradeIn(
        registration="AB-123-CD",
        mileage=50000,
        brand="Renault",
        model="Clio",
        estimated_value=Decimal("5000.00"),
    )

    dossier = Dossier.create(
        user_id=user.id,
        vehicle_id=vehicle.id,
        financing_plan=financing_plan,
        trade_in=trade_in,
    ).submit()
    await repository.save(dossier)
    await db_session.commit()

    response = await async_client.get(
        f"/api/v1/admin/dossiers/{dossier.id}",
        headers={"Authorization": f"Bearer {test_admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == str(dossier.id)
    assert data["financing_plan"] is not None
    assert data["financing_plan"]["down_payment"] == "2000.00"
    assert data["financing_plan"]["duration_months"] == 48
    assert data["financing_plan"]["monthly_payment"] == "395.50"

    assert data["trade_in"] is not None
    assert data["trade_in"]["registration"] == "AB-123-CD"
    assert data["trade_in"]["mileage"] == 50000
    assert data["trade_in"]["brand"] == "Renault"
    assert data["trade_in"]["model"] == "Clio"
    assert data["trade_in"]["estimated_value"] == "5000.00"


@pytest.mark.asyncio
async def test_get_dossier_detail_without_financing(
    async_client: AsyncClient,
    test_admin_token: str,
    db_session: AsyncSession,
) -> None:
    """Teste le détail d'un dossier sans financement."""
    repository = SQLAlchemyDossierRepository(db_session)
    user = await create_test_user(db_session, email="nofinancing@example.com")
    vehicle = await create_test_vehicle(db_session)

    dossier = Dossier.create(user_id=user.id, vehicle_id=vehicle.id).submit()
    await repository.save(dossier)
    await db_session.commit()

    response = await async_client.get(
        f"/api/v1/admin/dossiers/{dossier.id}",
        headers={"Authorization": f"Bearer {test_admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["financing_plan"] is None


@pytest.mark.asyncio
async def test_get_dossier_detail_without_trade_in(
    async_client: AsyncClient,
    test_admin_token: str,
    db_session: AsyncSession,
) -> None:
    """Teste le détail d'un dossier sans reprise."""
    repository = SQLAlchemyDossierRepository(db_session)
    user = await create_test_user(db_session, email="notradein@example.com")
    vehicle = await create_test_vehicle(db_session)

    dossier = Dossier.create(user_id=user.id, vehicle_id=vehicle.id).submit()
    await repository.save(dossier)
    await db_session.commit()

    response = await async_client.get(
        f"/api/v1/admin/dossiers/{dossier.id}",
        headers={"Authorization": f"Bearer {test_admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["trade_in"] is None


@pytest.mark.asyncio
async def test_get_dossier_detail_trade_in_without_estimated_value(
    async_client: AsyncClient,
    test_admin_token: str,
    db_session: AsyncSession,
) -> None:
    """Teste le détail d'un dossier avec reprise sans estimation."""
    repository = SQLAlchemyDossierRepository(db_session)
    user = await create_test_user(db_session, email="noestimate@example.com")
    vehicle = await create_test_vehicle(db_session)

    trade_in = TradeIn(
        registration="XY-987-ZW",
        mileage=75000,
        brand="Citroën",
        model="C3",
        estimated_value=None,
    )

    dossier = Dossier.create(
        user_id=user.id,
        vehicle_id=vehicle.id,
        trade_in=trade_in,
    ).submit()
    await repository.save(dossier)
    await db_session.commit()

    response = await async_client.get(
        f"/api/v1/admin/dossiers/{dossier.id}",
        headers={"Authorization": f"Bearer {test_admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["trade_in"] is not None
    assert data["trade_in"]["estimated_value"] is None


@pytest.mark.asyncio
async def test_get_dossier_detail_decimal_values(
    async_client: AsyncClient,
    test_admin_token: str,
    db_session: AsyncSession,
) -> None:
    """Vérifie que les valeurs décimales sont correctement sérialisées."""
    repository = SQLAlchemyDossierRepository(db_session)
    user = await create_test_user(db_session, email="decimal@example.com")
    vehicle = await create_test_vehicle(db_session)

    financing_plan = FinancingPlan(
        down_payment=Decimal("1500.99"),
        duration_months=60,
        monthly_payment=Decimal("299.99"),
    )

    dossier = Dossier.create(
        user_id=user.id,
        vehicle_id=vehicle.id,
        financing_plan=financing_plan,
    ).submit()
    await repository.save(dossier)
    await db_session.commit()

    response = await async_client.get(
        f"/api/v1/admin/dossiers/{dossier.id}",
        headers={"Authorization": f"Bearer {test_admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["financing_plan"]["down_payment"] == "1500.99"
    assert data["financing_plan"]["monthly_payment"] == "299.99"


@pytest.mark.asyncio
async def test_get_dossier_detail_forbidden_for_non_admin(
    async_client: AsyncClient,
    test_user_token: str,
    db_session: AsyncSession,
) -> None:
    """Vérifie qu'un client non-admin ne peut pas accéder au détail."""
    repository = SQLAlchemyDossierRepository(db_session)
    user = await create_test_user(db_session, email="forbidden@example.com")
    vehicle = await create_test_vehicle(db_session)

    dossier = Dossier.create(user_id=user.id, vehicle_id=vehicle.id).submit()
    await repository.save(dossier)
    await db_session.commit()

    response = await async_client.get(
        f"/api/v1/admin/dossiers/{dossier.id}",
        headers={"Authorization": f"Bearer {test_user_token}"},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_dossier_detail_nonexistent_returns_404(
    async_client: AsyncClient,
    test_admin_token: str,
) -> None:
    """Vérifie qu'un dossier inexistant retourne 404."""
    fake_id = uuid4()
    response = await async_client.get(
        f"/api/v1/admin/dossiers/{fake_id}",
        headers={"Authorization": f"Bearer {test_admin_token}"},
    )

    assert response.status_code == 404
