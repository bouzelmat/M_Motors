from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from src.dossiers.application.commands.create_dossier import (
    CreateDossierCommand,
    CreateDossierCommandHandler,
)
from src.dossiers.domain.entities.dossier import Dossier
from src.dossiers.domain.value_objects.dossier_status import DossierStatus
from src.dossiers.domain.value_objects.financing_plan import FinancingPlan
from src.dossiers.domain.value_objects.trade_in import TradeIn
from src.shared.domain.exceptions import DomainError


class FakeDossierRepository:
    """Repository mémoire utilisé pour tester sans base de données."""

    def __init__(self) -> None:
        self.saved_dossiers: list[Dossier] = []

    async def save(self, dossier: Dossier) -> None:
        self.saved_dossiers.append(dossier)


class FakeUnitOfWork:
    """Unit of Work mémoire utilisé pour vérifier le commit."""

    def __init__(self) -> None:
        self.committed = False

    async def __aenter__(self) -> "FakeUnitOfWork":
        return self

    async def __aexit__(
        self, exc_type: object, exc_val: object, exc_tb: object
    ) -> None:
        return None

    async def commit(self) -> None:
        self.committed = True


def test_create_builds_draft_dossier() -> None:
    user_id = uuid4()
    vehicle_id = uuid4()
    dossier = Dossier.create(user_id=user_id, vehicle_id=vehicle_id)
    assert dossier.user_id == user_id
    assert dossier.vehicle_id == vehicle_id
    assert dossier.status == DossierStatus.DRAFT
    assert dossier.upload_started_at is None
    assert dossier.trade_in is None
    assert dossier.financing_plan is None
    assert dossier.created_at.tzinfo == timezone.utc
    assert dossier.updated_at.tzinfo == timezone.utc


def test_create_builds_draft_dossier_with_trade_in_and_financing_plan() -> None:
    user_id = uuid4()
    vehicle_id = uuid4()
    trade_in = TradeIn(
        registration="AA-123-AA",
        mileage=45000,
        brand="Peugeot",
        model="208",
        estimated_value=Decimal("8500.00"),
    )
    financing_plan = FinancingPlan(
        down_payment=Decimal("2000.00"),
        duration_months=36,
        monthly_payment=Decimal("250.00"),
    )
    dossier = Dossier.create(
        user_id=user_id,
        vehicle_id=vehicle_id,
        trade_in=trade_in,
        financing_plan=financing_plan,
    )
    assert dossier.trade_in == trade_in
    assert dossier.financing_plan == financing_plan


def test_is_owned_by_returns_expected_result() -> None:
    owner_id = uuid4()
    dossier = Dossier.create(user_id=owner_id, vehicle_id=uuid4())
    assert dossier.is_owned_by(owner_id) is True
    assert dossier.is_owned_by(uuid4()) is False


def test_financing_plan_valid_instantiation() -> None:
    plan = FinancingPlan(
        down_payment=Decimal("1000.00"),
        duration_months=24,
        monthly_payment=Decimal("150.00"),
    )
    assert plan.down_payment == Decimal("1000.00")
    assert plan.duration_months == 24
    assert plan.monthly_payment == Decimal("150.00")


def test_financing_plan_negative_down_payment_raises_domain_error() -> None:
    with pytest.raises(DomainError, match="L'apport initial ne peut pas être négatif"):
        FinancingPlan(
            down_payment=Decimal("-100.00"),
            duration_months=24,
            monthly_payment=Decimal("150.00"),
        )


def test_financing_plan_invalid_duration_raises_domain_error() -> None:
    with pytest.raises(
        DomainError, match="La durée du financement doit être supérieure à 0"
    ):
        FinancingPlan(
            down_payment=Decimal("1000.00"),
            duration_months=0,
            monthly_payment=Decimal("150.00"),
        )


def test_financing_plan_negative_monthly_payment_raises_domain_error() -> None:
    with pytest.raises(DomainError, match="La mensualité ne peut pas être négative"):
        FinancingPlan(
            down_payment=Decimal("1000.00"),
            duration_months=24,
            monthly_payment=Decimal("-50.00"),
        )


def test_trade_in_valid_instantiation() -> None:
    trade_in = TradeIn(registration="AB-123-CD", mileage=120000)
    assert trade_in.registration == "AB-123-CD"
    assert trade_in.mileage == 120000


def test_trade_in_empty_registration_raises_domain_error() -> None:
    with pytest.raises(
        DomainError,
        match="L'immatriculation du véhicule de reprise ne peut pas être vide",
    ):
        TradeIn(registration="   ", mileage=50000)


def test_trade_in_negative_mileage_raises_domain_error() -> None:
    with pytest.raises(
        DomainError,
        match="Le kilométrage du véhicule de reprise ne peut pas être négatif",
    ):
        TradeIn(registration="AB-123-CD", mileage=-10)


def test_expire_draft_dossier() -> None:
    dossier = Dossier.create(user_id=uuid4(), vehicle_id=uuid4())
    now = datetime.now(timezone.utc)
    expired_dossier = dossier.expire(now=now)
    assert expired_dossier.status == DossierStatus.EXPIRED
    assert expired_dossier.updated_at == now


def test_expire_non_draft_dossier_raises_domain_error() -> None:
    dossier = Dossier.create(user_id=uuid4(), vehicle_id=uuid4())
    expired_dossier = dossier.expire()
    with pytest.raises(
        DomainError, match="Impossible d'expirer un dossier au statut EXPIRED"
    ):
        expired_dossier.expire()


@pytest.mark.asyncio
async def test_create_handler_saves_draft_and_commits() -> None:
    repository = FakeDossierRepository()
    uow = FakeUnitOfWork()
    handler = CreateDossierCommandHandler(
        dossier_repository=repository,
        uow=uow,
    )
    command = CreateDossierCommand(user_id=uuid4(), vehicle_id=uuid4())
    dossier = await handler.handle(command)
    assert dossier.status == DossierStatus.DRAFT
    assert repository.saved_dossiers == [dossier]
    assert uow.committed is True


# === NOUVEAUX TESTS POUR US-502 ===


def test_approve_submitted_dossier_transitions_to_validated() -> None:
    admin_id = uuid4()
    dossier = Dossier.create(user_id=uuid4(), vehicle_id=uuid4()).submit()
    now = datetime.now(timezone.utc)
    approved = dossier.approve(admin_id=admin_id, comment="Dossier complet", now=now)
    assert approved.status == DossierStatus.VALIDATED
    assert approved.comment == "Dossier complet"
    assert approved.validated_by_admin_id == admin_id
    assert approved.updated_at == now


def test_approve_non_submitted_dossier_raises_domain_error() -> None:
    admin_id = uuid4()
    dossier = Dossier.create(user_id=uuid4(), vehicle_id=uuid4())
    with pytest.raises(
        DomainError, match="Impossible de valider un dossier au statut DRAFT"
    ):
        dossier.approve(admin_id=admin_id)


def test_reject_submitted_dossier_transitions_to_rejected() -> None:
    admin_id = uuid4()
    dossier = Dossier.create(user_id=uuid4(), vehicle_id=uuid4()).submit()
    now = datetime.now(timezone.utc)
    rejected = dossier.reject(admin_id=admin_id, reason="Documents illisibles", now=now)
    assert rejected.status == DossierStatus.REJECTED
    assert rejected.rejection_reason == "Documents illisibles"
    assert rejected.rejected_by_admin_id == admin_id
    assert rejected.rejected_at == now
    assert rejected.updated_at == now


def test_reject_with_empty_reason_raises_domain_error() -> None:
    admin_id = uuid4()
    dossier = Dossier.create(user_id=uuid4(), vehicle_id=uuid4()).submit()
    with pytest.raises(DomainError, match="Le motif de rejet ne peut pas être vide"):
        dossier.reject(admin_id=admin_id, reason="")


def test_reject_with_whitespace_reason_raises_domain_error() -> None:
    admin_id = uuid4()
    dossier = Dossier.create(user_id=uuid4(), vehicle_id=uuid4()).submit()
    with pytest.raises(DomainError, match="Le motif de rejet ne peut pas être vide"):
        dossier.reject(admin_id=admin_id, reason="   ")


def test_reject_non_submitted_dossier_raises_domain_error() -> None:
    admin_id = uuid4()
    dossier = Dossier.create(user_id=uuid4(), vehicle_id=uuid4())
    with pytest.raises(
        DomainError, match="Impossible de rejeter un dossier au statut DRAFT"
    ):
        dossier.reject(admin_id=admin_id, reason="Motif valable")


def test_request_documents_from_submitted_transitions_to_documents_pending() -> None:
    dossier = Dossier.create(user_id=uuid4(), vehicle_id=uuid4()).submit()
    now = datetime.now(timezone.utc)
    updated = dossier.request_documents(
        document_types=["IDENTITY_CARD", "PAYSLIP"], now=now
    )
    assert updated.status == DossierStatus.DOCUMENTS_PENDING
    assert updated.requested_document_types == ["IDENTITY_CARD", "PAYSLIP"]
    assert updated.updated_at == now


def test_request_documents_from_documents_pending_remains_in_documents_pending() -> (
    None
):
    dossier = (
        Dossier.create(user_id=uuid4(), vehicle_id=uuid4())
        .submit()
        .request_documents(document_types=["IDENTITY_CARD"])
    )
    now = datetime.now(timezone.utc)
    updated = dossier.request_documents(
        document_types=["PROOF_OF_ADDRESS", "PAYSLIP"], now=now
    )
    assert updated.status == DossierStatus.DOCUMENTS_PENDING
    assert updated.requested_document_types == ["PROOF_OF_ADDRESS", "PAYSLIP"]


def test_request_documents_with_empty_list_raises_domain_error() -> None:
    dossier = Dossier.create(user_id=uuid4(), vehicle_id=uuid4()).submit()
    with pytest.raises(
        DomainError, match="La liste des documents demandés ne peut pas être vide"
    ):
        dossier.request_documents(document_types=[])


def test_request_documents_from_validated_raises_domain_error() -> None:
    admin_id = uuid4()
    dossier = Dossier.create(user_id=uuid4(), vehicle_id=uuid4()).submit()
    validated = dossier.approve(admin_id=admin_id)
    with pytest.raises(
        DomainError,
        match="Impossible de demander des documents pour un dossier au statut VALIDATED",
    ):
        validated.request_documents(document_types=["IDENTITY_CARD"])


def test_transitions_return_new_instance_without_mutating_original() -> None:
    admin_id = uuid4()
    original = Dossier.create(user_id=uuid4(), vehicle_id=uuid4()).submit()
    approved = original.approve(admin_id=admin_id)
    assert original.status == DossierStatus.SUBMITTED
    assert approved.status == DossierStatus.VALIDATED
    assert original is not approved
