from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.dossiers.domain.value_objects.dossier_status import DossierStatus
from src.dossiers.infrastructure.orm.dossier_model import DossierModel
from src.dossiers.infrastructure.adapters.dossier_existence_adapter import (
    DossierExistenceAdapter,
)


@pytest.mark.asyncio
async def test_has_active_dossier_submitted(db_session: AsyncSession) -> None:
    """Scénario : Dossier SUBMITTED lié au véhicule -> True."""
    vehicle_id = uuid4()
    dossier = DossierModel(
        id=uuid4(),
        user_id=uuid4(),
        vehicle_id=vehicle_id,
        status=DossierStatus.SUBMITTED,
    )
    db_session.add(dossier)
    await db_session.flush()

    adapter = DossierExistenceAdapter(session=db_session)
    result = await adapter.has_active_dossier_for_vehicle(vehicle_id)

    assert result is True


@pytest.mark.asyncio
async def test_has_active_dossier_documents_pending(db_session: AsyncSession) -> None:
    vehicle_id = uuid4()
    db_session.add(
        DossierModel(
            id=uuid4(),
            user_id=uuid4(),
            vehicle_id=vehicle_id,
            status=DossierStatus.DOCUMENTS_PENDING,
        )
    )
    await db_session.flush()

    adapter = DossierExistenceAdapter(session=db_session)
    assert await adapter.has_active_dossier_for_vehicle(vehicle_id) is True


@pytest.mark.asyncio
async def test_has_active_dossier_draft_unexpired(db_session: AsyncSession) -> None:
    """Scénario : Dossier DRAFT non expiré lié au véhicule -> True."""
    vehicle_id = uuid4()
    dossier = DossierModel(
        id=uuid4(),
        user_id=uuid4(),
        vehicle_id=vehicle_id,
        status=DossierStatus.DRAFT,
        upload_started_at=datetime.now(timezone.utc) - timedelta(minutes=10),
    )
    db_session.add(dossier)
    await db_session.flush()

    adapter = DossierExistenceAdapter(session=db_session)
    result = await adapter.has_active_dossier_for_vehicle(vehicle_id)

    assert result is True


@pytest.mark.asyncio
async def test_has_active_dossier_expired(db_session: AsyncSession) -> None:
    """Scénario : Dossier EXPIRED lié au véhicule -> False."""
    vehicle_id = uuid4()
    dossier = DossierModel(
        id=uuid4(),
        user_id=uuid4(),
        vehicle_id=vehicle_id,
        status=DossierStatus.EXPIRED,
        upload_started_at=datetime.now(timezone.utc) - timedelta(minutes=50),
    )
    db_session.add(dossier)
    await db_session.flush()

    adapter = DossierExistenceAdapter(session=db_session)
    result = await adapter.has_active_dossier_for_vehicle(vehicle_id)

    assert result is False


@pytest.mark.asyncio
async def test_has_active_dossier_validated_or_rejected(
    db_session: AsyncSession,
) -> None:
    """Scénario : Dossier VALIDATED ou REJECTED lié au véhicule -> False."""
    vehicle_id = uuid4()
    dossier_val = DossierModel(
        id=uuid4(),
        user_id=uuid4(),
        vehicle_id=vehicle_id,
        status=DossierStatus.VALIDATED,
    )
    dossier_rej = DossierModel(
        id=uuid4(),
        user_id=uuid4(),
        vehicle_id=vehicle_id,
        status=DossierStatus.REJECTED,
    )
    db_session.add_all([dossier_val, dossier_rej])
    await db_session.flush()

    adapter = DossierExistenceAdapter(session=db_session)
    result = await adapter.has_active_dossier_for_vehicle(vehicle_id)

    assert result is False


@pytest.mark.asyncio
async def test_has_active_dossier_none_linked(db_session: AsyncSession) -> None:
    """Scénario : Aucun dossier lié au véhicule -> False."""
    vehicle_id = uuid4()

    adapter = DossierExistenceAdapter(session=db_session)
    result = await adapter.has_active_dossier_for_vehicle(vehicle_id)

    assert result is False


@pytest.mark.asyncio
async def test_has_active_dossier_multiple_with_one_active(
    db_session: AsyncSession,
) -> None:
    """Scénario : Plusieurs dossiers, dont un actif -> True."""
    vehicle_id = uuid4()
    d1 = DossierModel(
        id=uuid4(),
        user_id=uuid4(),
        vehicle_id=vehicle_id,
        status=DossierStatus.REJECTED,
    )
    d2 = DossierModel(
        id=uuid4(),
        user_id=uuid4(),
        vehicle_id=vehicle_id,
        status=DossierStatus.SUBMITTED,
    )
    db_session.add_all([d1, d2])
    await db_session.flush()

    adapter = DossierExistenceAdapter(session=db_session)
    result = await adapter.has_active_dossier_for_vehicle(vehicle_id)

    assert result is True


@pytest.mark.asyncio
async def test_has_active_dossier_shared_uow_session(db_session: AsyncSession) -> None:
    """Scénario : Session partagée avec l'Unit of Work (utilisation de la même AsyncSession)."""
    vehicle_id = uuid4()

    adapter = DossierExistenceAdapter(session=db_session)
    assert adapter._session is db_session

    result = await adapter.has_active_dossier_for_vehicle(vehicle_id)
    assert result is False
