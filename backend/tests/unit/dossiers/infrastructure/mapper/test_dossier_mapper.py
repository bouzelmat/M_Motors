"""Tests unitaires pour le mapper DossierMapper."""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4


from src.dossiers.domain.entities.dossier import Dossier
from src.dossiers.domain.value_objects.dossier_status import DossierStatus
from src.dossiers.domain.value_objects.financing_plan import FinancingPlan
from src.dossiers.domain.value_objects.trade_in import TradeIn
from src.dossiers.infrastructure.orm.dossier_model import DossierModel
from src.dossiers.infrastructure.orm.financing_plan_model import FinancingPlanModel
from src.dossiers.infrastructure.orm.trade_in_model import TradeInModel
from src.dossiers.infrastructure.mappers.dossier_mapper import DossierMapper


def test_to_domain_with_minimal_model() -> None:
    dossier_id = uuid4()
    user_id = uuid4()
    vehicle_id = uuid4()
    now = datetime.now(timezone.utc)

    model = DossierModel(
        id=dossier_id,
        user_id=user_id,
        vehicle_id=vehicle_id,
        status=DossierStatus.DRAFT,
        upload_started_at=None,
        created_at=now,
        updated_at=now,
        trade_in=None,
        financing_plan=None,
    )

    domain = DossierMapper.to_domain(model)

    assert domain.id == dossier_id
    assert domain.user_id == user_id
    assert domain.vehicle_id == vehicle_id
    assert domain.status == DossierStatus.DRAFT
    assert domain.upload_started_at is None
    assert domain.trade_in is None
    assert domain.financing_plan is None
    assert domain.created_at == now
    assert domain.updated_at == now


def test_to_domain_with_full_model() -> None:
    dossier_id = uuid4()
    now = datetime.now(timezone.utc)

    trade_in_model = TradeInModel(
        dossier_id=dossier_id,
        registration="AA-123-BB",
        mileage=35000,
        brand="Peugeot",
        model="208",
        estimated_value=Decimal("9500.00"),
    )
    financing_model = FinancingPlanModel(
        dossier_id=dossier_id,
        down_payment=Decimal("1500.00"),
        duration_months=36,
        monthly_payment=Decimal("180.00"),
    )
    model = DossierModel(
        id=dossier_id,
        user_id=uuid4(),
        vehicle_id=uuid4(),
        status=DossierStatus.SUBMITTED,
        upload_started_at=now,
        created_at=now,
        updated_at=now,
        trade_in=trade_in_model,
        financing_plan=financing_model,
    )

    domain = DossierMapper.to_domain(model)

    assert domain.trade_in == TradeIn(
        registration="AA-123-BB",
        mileage=35000,
        brand="Peugeot",
        model="208",
        estimated_value=Decimal("9500.00"),
    )
    assert domain.financing_plan == FinancingPlan(
        down_payment=Decimal("1500.00"),
        duration_months=36,
        monthly_payment=Decimal("180.00"),
    )


def test_to_orm_creates_new_model() -> None:
    trade_in = TradeIn(registration="XY-987-ZZ", mileage=12000)
    financing = FinancingPlan(
        down_payment=Decimal("500.00"),
        duration_months=12,
        monthly_payment=Decimal("300.00"),
    )
    dossier = Dossier.create(
        user_id=uuid4(),
        vehicle_id=uuid4(),
        trade_in=trade_in,
        financing_plan=financing,
    )

    model = DossierMapper.to_orm(dossier)

    assert model.id == dossier.id
    assert model.user_id == dossier.user_id
    assert model.vehicle_id == dossier.vehicle_id
    assert model.status == DossierStatus.DRAFT
    assert model.trade_in is not None
    assert model.trade_in.registration == "XY-987-ZZ"
    assert model.financing_plan is not None
    assert model.financing_plan.duration_months == 12


def test_to_orm_updates_existing_model_in_place() -> None:
    dossier_id = uuid4()
    existing_model = DossierModel(
        id=dossier_id,
        user_id=uuid4(),
        vehicle_id=uuid4(),
        status=DossierStatus.DRAFT,
        trade_in=TradeInModel(
            dossier_id=dossier_id,
            registration="OLD-REG",
            mileage=1000,
        ),
        financing_plan=None,
    )

    updated_trade_in = TradeIn(registration="NEW-REG", mileage=5000)
    updated_dossier = Dossier(
        id=dossier_id,
        user_id=existing_model.user_id,
        vehicle_id=existing_model.vehicle_id,
        status=DossierStatus.SUBMITTED,
        trade_in=updated_trade_in,
        financing_plan=None,
        upload_started_at=datetime.now(timezone.utc),
    )

    result_model = DossierMapper.to_orm(updated_dossier, existing_model)

    assert result_model is existing_model
    assert result_model.id == dossier_id
    assert result_model.status == DossierStatus.SUBMITTED
    assert result_model.trade_in.registration == "NEW-REG"
    assert result_model.trade_in.mileage == 5000


def test_roundtrip_domain_orm_domain() -> None:
    original = Dossier.create(
        user_id=uuid4(),
        vehicle_id=uuid4(),
        trade_in=TradeIn(registration="RT-100-OK", mileage=80000),
        financing_plan=FinancingPlan(
            down_payment=Decimal("0.00"),
            duration_months=48,
            monthly_payment=Decimal("120.00"),
        ),
    )

    orm_model = DossierMapper.to_orm(original)
    reconstructed = DossierMapper.to_domain(orm_model)

    assert reconstructed == original
