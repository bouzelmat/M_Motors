"""Tests de bout en bout (E2E) pour la consultation des dossiers en attente (US-501)."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.infrastructure.orm.user_model import UserModel
from src.auth.infrastructure.security.jwt_service import JWTService
from src.dossiers.domain.entities.dossier import Dossier
from src.dossiers.domain.value_objects.dossier_status import DossierStatus
from src.dossiers.infrastructure.repository.sqlalchemy_dossier_repository import (
    SQLAlchemyDossierRepository,
)
from src.vehicles.infrastructure.orm.vehicle_model import VehicleModel

# Imports ajoutés pour respecter les types Enum non-nullables du modèle VehicleModel
from src.vehicles.domain.value_objects.energy_type import EnergyType
from src.vehicles.domain.value_objects.vehicle_status import VehicleStatus
from src.vehicles.domain.value_objects.catalog_type import CatalogType


async def _create_user_in_db(
    session: AsyncSession, email: str, role: str = "CLIENT"
) -> UserModel:
    user = UserModel(
        id=uuid4(),
        email=email,
        hashed_password="fake_hashed_password",
        first_name="Jean",
        last_name="Dupont",
        role=role,
        is_active=True,
    )
    session.add(user)
    await session.flush()
    return user


async def _create_vehicle_in_db(
    session: AsyncSession, brand: str, model: str
) -> VehicleModel:
    vehicle = VehicleModel(
        id=uuid4(),
        brand=brand,
        model=model,
        year=2021,  # <-- Ajouté (nullable=False)
        mileage=30000,  # <-- Ajouté (nullable=False)
        energy_type=EnergyType.ESSENCE,  # <-- Ajouté (nullable=False)
        catalog_type=CatalogType.RENTAL,
        status=VehicleStatus.AVAILABLE,
        monthly_rent=350,
    )
    session.add(vehicle)
    await session.flush()
    return vehicle


@pytest.mark.asyncio
async def test_full_pending_dossiers_lifecycle_e2e(
    async_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    # 1. Préparation des acteurs et jetons JWT
    jwt_service = JWTService()

    admin_user = await _create_user_in_db(
        db_session, email="admin.test@mmotors.fr", role="ADMIN"
    )
    client_user_1 = await _create_user_in_db(
        db_session, email="client1.test@mmotors.fr", role="CLIENT"
    )
    client_user_2 = await _create_user_in_db(
        db_session, email="client2.test@mmotors.fr", role="CLIENT"
    )

    admin_token = jwt_service.create_access_token(
        data={"sub": str(admin_user.id), "role": "ADMIN"}
    )
    client_token = jwt_service.create_access_token(
        data={"sub": str(client_user_1.id), "role": "CLIENT"}
    )

    vehicle_1 = await _create_vehicle_in_db(db_session, "Peugeot", "208")
    vehicle_2 = await _create_vehicle_in_db(db_session, "BMW", "Série 3")

    repository = SQLAlchemyDossierRepository(db_session)
    now = datetime.now(timezone.utc)

    # 2. Création de 2 dossiers soumis à des dates différentes + 1 dossier brouillon
    dossier_old = Dossier.create(
        user_id=client_user_1.id, vehicle_id=vehicle_1.id
    ).submit(now=now - timedelta(hours=5))

    dossier_recent = Dossier.create(
        user_id=client_user_2.id, vehicle_id=vehicle_2.id
    ).submit(now=now - timedelta(minutes=15))

    dossier_draft = Dossier.create(user_id=client_user_1.id, vehicle_id=vehicle_2.id)

    await repository.save(dossier_old)
    await repository.save(dossier_recent)
    await repository.save(dossier_draft)
    await db_session.commit()

    # 3. Test de sécurité : Accès refusé pour un client classique (403 Forbidden)
    forbidden_res = await async_client.get(
        "/api/v1/admin/dossiers/pending",
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert forbidden_res.status_code == 403

    # 4. Test d'exécution Admin : Récupération des dossiers en attente
    admin_res = await async_client.get(
        "/api/v1/admin/dossiers/pending",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert admin_res.status_code == 200

    data = admin_res.json()

    # Seuls les 2 dossiers SUBMITTED doivent être renvoyés (le DRAFT est exclu)
    retrieved_ids = [item["id"] for item in data]
    assert str(dossier_recent.id) in retrieved_ids
    assert str(dossier_old.id) in retrieved_ids
    assert str(dossier_draft.id) not in retrieved_ids

    # Vérification du tri décroissant par défaut sur submitted_at
    item_first = next(i for i in data if i["id"] == str(dossier_recent.id))
    item_second = next(i for i in data if i["id"] == str(dossier_old.id))

    assert data.index(item_first) < data.index(item_second)

    # Vérification de l'exactitude des projections utilisateur et véhicule
    assert item_first["client_email"] == "client2.test@mmotors.fr"
    assert item_first["vehicle_brand"] == "BMW"
    assert item_first["vehicle_model"] == "Série 3"
    assert item_first["status"] == DossierStatus.SUBMITTED.value

    assert item_second["client_email"] == "client1.test@mmotors.fr"
    assert item_second["vehicle_brand"] == "Peugeot"
    assert item_second["vehicle_model"] == "208"
