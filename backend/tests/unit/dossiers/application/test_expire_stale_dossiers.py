from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID, uuid4

import pytest

from src.dossiers.application.commands.expire_stale_dossiers import (
    ExpireStaleDossiersCommand,
    ExpireStaleDossiersCommandHandler,
)
from src.dossiers.domain.constants import DRAFT_UPLOAD_TIMEOUT_MINUTES
from src.dossiers.domain.entities.dossier import Dossier
from src.dossiers.domain.events.dossier_expired import DossierExpired
from src.dossiers.domain.ports.dossier_repository import DossierRepository
from src.dossiers.domain.value_objects.dossier_status import DossierStatus


class FakeDossierRepository(DossierRepository):
    def __init__(self, dossiers: list[Dossier] | None = None) -> None:
        self.dossiers: dict[UUID, Dossier] = (
            {d.id: d for d in dossiers} if dossiers else {}
        )

    async def get_by_id(self, dossier_id: UUID) -> Dossier | None:
        return self.dossiers.get(dossier_id)

    async def save(self, dossier: Dossier) -> None:
        self.dossiers[dossier.id] = dossier

    async def get_stale_draft_dossiers(self, cutoff_time: datetime) -> list[Dossier]:
        return [
            d
            for d in self.dossiers.values()
            if d.status == DossierStatus.DRAFT
            and d.upload_started_at is not None
            and d.upload_started_at <= cutoff_time
        ]


class FakeUnitOfWork:
    def __init__(self) -> None:
        self.committed = False

    async def __aenter__(self) -> "FakeUnitOfWork":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        pass

    async def commit(self) -> None:
        self.committed = True


class FakeEventBus:
    def __init__(self) -> None:
        self.published_events: list[Any] = []

    async def publish(self, event: Any) -> None:
        self.published_events.append(event)


@pytest.fixture
def now() -> datetime:
    return datetime(2026, 9, 12, 10, 0, 0, tzinfo=timezone.utc)


def test_mark_upload_started_only_sets_once(now: datetime) -> None:
    """Scénario : Premier document déclenche le compteur."""
    dossier = Dossier(
        id=uuid4(),
        user_id=uuid4(),
        vehicle_id=uuid4(),
        status=DossierStatus.DRAFT,
    )
    assert dossier.upload_started_at is None

    first_upload_time = now
    dossier_updated = dossier.mark_upload_started(now=first_upload_time)
    assert dossier_updated.upload_started_at == first_upload_time

    second_upload_time = now + timedelta(minutes=10)
    dossier_reupdated = dossier_updated.mark_upload_started(now=second_upload_time)
    # L'horodatage ne doit pas changer
    assert dossier_reupdated.upload_started_at == first_upload_time


@pytest.mark.asyncio
async def test_expire_stale_dossiers_success(now: datetime) -> None:
    """Scénario : Expiration après dépassement du délai (40 minutes)."""
    stale_time = now - timedelta(minutes=DRAFT_UPLOAD_TIMEOUT_MINUTES + 5)
    stale_dossier = Dossier(
        id=uuid4(),
        user_id=uuid4(),
        vehicle_id=uuid4(),
        status=DossierStatus.DRAFT,
        upload_started_at=stale_time,
    )

    repo = FakeDossierRepository([stale_dossier])
    uow = FakeUnitOfWork()
    bus = FakeEventBus()
    handler = ExpireStaleDossiersCommandHandler(repository=repo, uow=uow, event_bus=bus)

    count = await handler.handle(ExpireStaleDossiersCommand(now=now))

    assert count == 1
    updated = await repo.get_by_id(stale_dossier.id)
    assert updated.status == DossierStatus.EXPIRED
    assert uow.committed is True
    assert len(bus.published_events) == 1
    assert isinstance(bus.published_events[0], DossierExpired)
    assert bus.published_events[0].dossier_id == stale_dossier.id


@pytest.mark.asyncio
async def test_no_premature_expiration(now: datetime) -> None:
    """Scénario : Pas d'expiration prématurée pour un dossier de moins de 40 minutes."""
    recent_time = now - timedelta(minutes=DRAFT_UPLOAD_TIMEOUT_MINUTES - 5)
    recent_dossier = Dossier(
        id=uuid4(),
        user_id=uuid4(),
        vehicle_id=uuid4(),
        status=DossierStatus.DRAFT,
        upload_started_at=recent_time,
    )

    repo = FakeDossierRepository([recent_dossier])
    uow = FakeUnitOfWork()
    bus = FakeEventBus()
    handler = ExpireStaleDossiersCommandHandler(repository=repo, uow=uow, event_bus=bus)

    count = await handler.handle(ExpireStaleDossiersCommand(now=now))

    assert count == 0
    updated = await repo.get_by_id(recent_dossier.id)
    assert updated.status == DossierStatus.DRAFT
    assert len(bus.published_events) == 0


@pytest.mark.asyncio
async def test_submitted_dossiers_not_affected(now: datetime) -> None:
    """Scénario : Dossier soumis à temps, non concerné."""
    old_time = now - timedelta(minutes=DRAFT_UPLOAD_TIMEOUT_MINUTES + 20)
    submitted_dossier = Dossier(
        id=uuid4(),
        user_id=uuid4(),
        vehicle_id=uuid4(),
        status=DossierStatus.SUBMITTED,
        upload_started_at=old_time,
    )

    repo = FakeDossierRepository([submitted_dossier])
    uow = FakeUnitOfWork()
    bus = FakeEventBus()
    handler = ExpireStaleDossiersCommandHandler(repository=repo, uow=uow, event_bus=bus)

    count = await handler.handle(ExpireStaleDossiersCommand(now=now))

    assert count == 0
    updated = await repo.get_by_id(submitted_dossier.id)
    assert updated.status == DossierStatus.SUBMITTED


@pytest.mark.asyncio
async def test_job_idempotency(now: datetime) -> None:
    """Scénario : Idempotence du job (les dossiers déjà EXPIRED ne déclenchent pas d'événement)."""
    expired_dossier = Dossier(
        id=uuid4(),
        user_id=uuid4(),
        vehicle_id=uuid4(),
        status=DossierStatus.EXPIRED,
        upload_started_at=now - timedelta(minutes=100),
    )

    repo = FakeDossierRepository([expired_dossier])
    uow = FakeUnitOfWork()
    bus = FakeEventBus()
    handler = ExpireStaleDossiersCommandHandler(repository=repo, uow=uow, event_bus=bus)

    count = await handler.handle(ExpireStaleDossiersCommand(now=now))

    assert count == 0
    assert len(bus.published_events) == 0


@pytest.mark.asyncio
async def test_job_execution_idempotency_sequential_calls(now: datetime) -> None:
    """Scénario : Exécution consécutive du job. La seconde exécution ne produit aucun effet."""
    stale_time = now - timedelta(minutes=DRAFT_UPLOAD_TIMEOUT_MINUTES + 10)
    stale_dossier = Dossier(
        id=uuid4(),
        user_id=uuid4(),
        vehicle_id=uuid4(),
        status=DossierStatus.DRAFT,
        upload_started_at=stale_time,
    )

    repo = FakeDossierRepository([stale_dossier])
    uow = FakeUnitOfWork()
    bus = FakeEventBus()
    handler = ExpireStaleDossiersCommandHandler(repository=repo, uow=uow, event_bus=bus)

    # Première exécution : Doit expirer le dossier et émettre l'événement
    first_run_count = await handler.handle(ExpireStaleDossiersCommand(now=now))
    assert first_run_count == 1
    assert len(bus.published_events) == 1

    # Réinitialisation de l'espion du bus d'événements
    bus.published_events.clear()

    # Seconde exécution consécutive à T + 1 min : Doit être neutre (0 dossiers traités)
    second_run_count = await handler.handle(
        ExpireStaleDossiersCommand(now=now + timedelta(minutes=1))
    )
    assert second_run_count == 0
    assert len(bus.published_events) == 0

    # Vérification que le statut reste EXPIRED
    final_dossier = await repo.get_by_id(stale_dossier.id)
    assert final_dossier.status == DossierStatus.EXPIRED
