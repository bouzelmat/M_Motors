from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dossiers.domain.entities.dossier import Dossier
from src.dossiers.domain.value_objects.dossier_status import DossierStatus
from src.dossiers.domain.value_objects.financing_plan import FinancingPlan
from src.dossiers.domain.value_objects.trade_in import TradeIn
from src.dossiers.infrastructure.models.dossier_model import DossierModel
from src.dossiers.infrastructure.persistence.dossier_repository import (
    SQLAlchemyDossierRepository,
)


@pytest.mark.asyncio
async def test_get_by_id_returns_none_when_not_found(db_session: AsyncSession) -> None:
    repository = SQLAlchemyDossierRepository(db_session)

    result = await repository.get_by_id(uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_save_and_get_minimal_dossier(db_session: AsyncSession) -> None:
    repository = SQLAlchemyDossierRepository(db_session)
    dossier = Dossier.create(user_id=uuid4(), vehicle_id=uuid4())

    await repository.save(dossier)
    await db_session.commit()

    retrieved = await repository.get_by_id(dossier.id)

    assert retrieved is not None
    assert retrieved.id == dossier.id
    assert retrieved.trade_in is None
    assert retrieved.financing_plan is None


@pytest.mark.asyncio
async def test_save_and_get_dossier_with_trade_in_and_financing(
    db_session: AsyncSession,
) -> None:
    repository = SQLAlchemyDossierRepository(db_session)
    trade_in = TradeIn(
        registration="AB-123-CD",
        mileage=50000,
        brand="Renault",
        model="Clio",
        estimated_value=Decimal("5000.00"),
    )
    financing_plan = FinancingPlan(
        down_payment=Decimal("1000.00"),
        duration_months=24,
        monthly_payment=Decimal("200.00"),
    )
    dossier = Dossier.create(
        user_id=uuid4(),
        vehicle_id=uuid4(),
        trade_in=trade_in,
        financing_plan=financing_plan,
    )

    await repository.save(dossier)
    await db_session.commit()

    retrieved = await repository.get_by_id(dossier.id)

    assert retrieved is not None
    assert retrieved.trade_in == trade_in
    assert retrieved.financing_plan == financing_plan


@pytest.mark.asyncio
async def test_update_existing_dossier_in_repository(db_session: AsyncSession) -> None:
    repository = SQLAlchemyDossierRepository(db_session)
    dossier = Dossier.create(user_id=uuid4(), vehicle_id=uuid4())

    await repository.save(dossier)
    await db_session.commit()

    # Mise à jour de l'agrégat
    updated_dossier = dossier.mark_upload_started()
    await repository.save(updated_dossier)
    await db_session.commit()

    retrieved = await repository.get_by_id(dossier.id)
    assert retrieved is not None
    assert retrieved.upload_started_at is not None


@pytest.mark.asyncio
async def test_save_idempotency_does_not_duplicate_records(
    db_session: AsyncSession,
) -> None:
    repository = SQLAlchemyDossierRepository(db_session)
    dossier = Dossier.create(user_id=uuid4(), vehicle_id=uuid4())

    # Sauvegardes successives répétées
    await repository.save(dossier)
    await repository.save(dossier)
    await db_session.commit()

    result = await db_session.execute(
        select(DossierModel).where(DossierModel.id == dossier.id)
    )
    models = result.scalars().all()

    assert len(models) == 1


@pytest.mark.asyncio
async def test_has_active_for_vehicle_with_statuses(db_session: AsyncSession) -> None:
    repository = SQLAlchemyDossierRepository(db_session)
    vehicle_id = uuid4()

    # Statut DRAFT
    draft_dossier = Dossier.create(user_id=uuid4(), vehicle_id=vehicle_id)
    await repository.save(draft_dossier)
    await db_session.commit()

    assert await repository.has_active_for_vehicle(vehicle_id) is True

    # Statut EXPIRED (ne doit plus être actif)
    expired_dossier = draft_dossier.expire()
    await repository.save(expired_dossier)
    await db_session.commit()

    assert await repository.has_active_for_vehicle(vehicle_id) is False


@pytest.mark.asyncio
async def test_get_stale_draft_dossiers_filtering(db_session: AsyncSession) -> None:
    repository = SQLAlchemyDossierRepository(db_session)
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=24)

    stale_dossier = Dossier.create(user_id=uuid4(), vehicle_id=uuid4())
    stale_dossier = stale_dossier.mark_upload_started(now=now - timedelta(hours=25))

    recent_dossier = Dossier.create(user_id=uuid4(), vehicle_id=uuid4())
    recent_dossier = recent_dossier.mark_upload_started(now=now - timedelta(hours=1))

    await repository.save(stale_dossier)
    await repository.save(recent_dossier)
    await db_session.commit()

    stale_list = await repository.get_stale_draft_dossiers(cutoff_time=cutoff)
    stale_ids = [d.id for d in stale_list]

    assert stale_dossier.id in stale_ids
    assert recent_dossier.id not in stale_ids