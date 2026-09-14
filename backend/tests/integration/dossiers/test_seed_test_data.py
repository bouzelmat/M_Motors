"""Tests d'intégration pour le script de seed des données de test E2E."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from scripts.seed_test_data import (
    ACTIVE_DOSSIER_ID,
    RENAULT_ID,
    TEST_USER_ID,
    seed_vehicles,
)
from src.dossiers.domain.value_objects.dossier_status import DossierStatus
from src.dossiers.infrastructure.adapters.dossier_existence_adapter import (
    DossierExistenceAdapter,
)
from src.dossiers.infrastructure.models.dossier_model import DossierModel
from src.vehicles.infrastructure.orm.vehicle_model import VehicleModel


@pytest.mark.asyncio
async def test_seed_test_data_creates_active_dossier(db_session: AsyncSession) -> None:
    """Vérifie que l'exécution du seed crée les données attendues et le dossier actif."""
    # Exécution du script de seed en réutilisant la session isolée du test
    await seed_vehicles(db_session)

    # 1. Vérification que le véhicule de référence existe
    stmt_vehicle = select(VehicleModel).where(VehicleModel.id == RENAULT_ID)
    res_vehicle = await db_session.execute(stmt_vehicle)
    vehicle = res_vehicle.scalar_one_or_none()
    assert vehicle is not None
    assert vehicle.brand == "Renault"

    # 2. Vérification de la création du dossier actif
    stmt_dossier = select(DossierModel).where(DossierModel.id == ACTIVE_DOSSIER_ID)
    res_dossier = await db_session.execute(stmt_dossier)
    dossier = res_dossier.scalar_one_or_none()

    assert dossier is not None
    assert dossier.vehicle_id == RENAULT_ID
    assert dossier.user_id == TEST_USER_ID
    assert dossier.status == DossierStatus.SUBMITTED
    assert dossier.upload_started_at is None

    # 3. Vérification de la détection par l'adaptateur métier
    adapter = DossierExistenceAdapter(session=db_session)
    has_active = await adapter.has_active_dossier_for_vehicle(RENAULT_ID)
    assert has_active is True


@pytest.mark.asyncio
async def test_seed_test_data_idempotency(db_session: AsyncSession) -> None:
    """Vérifie que deux exécutions consécutives du seed restent idempotentes et ne dupliquent pas les entrées."""
    await seed_vehicles(db_session)
    await seed_vehicles(db_session)

    stmt_dossier = select(DossierModel).where(DossierModel.vehicle_id == RENAULT_ID)
    res_dossier = await db_session.execute(stmt_dossier)
    dossiers = res_dossier.scalars().all()

    # Un seul dossier actif doit exister pour RENAULT_ID
    assert len(dossiers) == 1
    assert dossiers[0].id == ACTIVE_DOSSIER_ID
