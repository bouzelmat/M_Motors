from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4, UUID

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.infrastructure.orm.user_model import UserModel
from src.dossiers.domain.entities.dossier import Dossier
from src.dossiers.domain.value_objects.dossier_status import DossierStatus
from src.dossiers.domain.value_objects.financing_plan import FinancingPlan
from src.dossiers.domain.value_objects.trade_in import TradeIn
from src.dossiers.infrastructure.orm.dossier_model import DossierModel
from src.dossiers.infrastructure.repository.sqlalchemy_dossier_repository import (
    SQLAlchemyDossierRepository,
)
from src.vehicles.infrastructure.orm.vehicle_model import VehicleModel
from src.vehicles.domain.value_objects.catalog_type import CatalogType
from src.vehicles.domain.value_objects.energy_type import EnergyType
from src.vehicles.domain.value_objects.vehicle_status import VehicleStatus


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
async def test_save_updates_dossier_when_relationships_are_expired(
    db_session: AsyncSession,
) -> None:
    repository = SQLAlchemyDossierRepository(db_session)
    dossier = Dossier.create(
        user_id=uuid4(),
        vehicle_id=uuid4(),
        financing_plan=FinancingPlan(
            down_payment=Decimal("1000.00"),
            duration_months=24,
            monthly_payment=Decimal("200.00"),
        ),
    )

    await repository.save(dossier)
    await db_session.commit()

    model = await db_session.get(DossierModel, dossier.id)
    assert model is not None
    db_session.expire(model, ["trade_in", "financing_plan"])

    submitted_dossier = dossier.submit()
    await repository.save(submitted_dossier)
    await db_session.commit()

    retrieved = await repository.get_by_id(dossier.id)
    assert retrieved is not None
    assert retrieved.status == DossierStatus.SUBMITTED
    assert retrieved.financing_plan == dossier.financing_plan


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


async def _create_test_user_and_vehicle(
    db_session: AsyncSession, email: str, brand: str, model_name: str
) -> tuple[UUID, UUID]:
    user_id = uuid4()
    vehicle_id = uuid4()

    user = UserModel(
        id=user_id,
        email=email,
        hashed_password="hashed_pw",
        first_name="John",
        last_name="Doe",
    )
    vehicle = VehicleModel(
        id=vehicle_id,
        brand=brand,
        model=model_name,
        year=2024,
        price=Decimal("25000.00"),
        mileage=15000,
        energy_type=EnergyType.ELECTRIQUE,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.RENTAL,
        monthly_rent=Decimal("350.00"),
    )
    db_session.add(user)
    db_session.add(vehicle)
    await db_session.flush()
    return user_id, vehicle_id


@pytest.mark.asyncio
async def test_list_pending_returns_only_submitted_dossiers_sorted(
    db_session: AsyncSession,
) -> None:
    repository = SQLAlchemyDossierRepository(db_session)
    user_id, vehicle_id = await _create_test_user_and_vehicle(
        db_session, "client1@example.com", "Peugeot", "208"
    )

    now = datetime.now(timezone.utc)

    # Dossier SUBMITTED il y a 2 heures
    dossier_submitted_1 = Dossier.create(user_id=user_id, vehicle_id=vehicle_id).submit(
        now=now - timedelta(hours=2)
    )
    # Dossier SUBMITTED il y a 10 minutes
    dossier_submitted_2 = Dossier.create(user_id=user_id, vehicle_id=vehicle_id).submit(
        now=now - timedelta(minutes=10)
    )
    # Dossier DRAFT (exclu)
    dossier_draft = Dossier.create(user_id=user_id, vehicle_id=vehicle_id)

    await repository.save(dossier_submitted_1)
    await repository.save(dossier_submitted_2)
    await repository.save(dossier_draft)
    await db_session.commit()

    pending_list = await repository.list_pending(sort_by="submitted_at")

    assert len(pending_list) == 2
    assert pending_list[0].id == dossier_submitted_2.id
    assert pending_list[1].id == dossier_submitted_1.id
    assert pending_list[0].client_email == "client1@example.com"
    assert pending_list[0].vehicle_brand == "Peugeot"
    assert pending_list[0].vehicle_model == "208"
    assert pending_list[0].status == DossierStatus.SUBMITTED


@pytest.mark.asyncio
async def test_list_pending_raises_value_error_on_invalid_sort(
    db_session: AsyncSession,
) -> None:
    """Test que list_pending lève ValueError pour un champ de tri invalide."""
    repository = SQLAlchemyDossierRepository(db_session)
    # 🔴 CORRECTION: Attendre ValueError au lieu de DomainError (car on a changé dans sqlalchemy_dossier_repository.py)
    with pytest.raises(ValueError, match="Invalid sort field"):
        await repository.list_pending(sort_by="invalid_field")
