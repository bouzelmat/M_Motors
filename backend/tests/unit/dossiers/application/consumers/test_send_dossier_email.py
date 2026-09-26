"""Tests unitaires des consommateurs de notification e-mail."""

import logging
from uuid import uuid4

import pytest

from src.dossiers.application.consumers.send_dossier_email import (
    SendDocumentsRequestedEmailConsumer,
    SendDossierRejectedEmailConsumer,
    SendDossierValidatedEmailConsumer,
)
from src.dossiers.domain.events.documents_requested import DocumentsRequested
from src.dossiers.domain.events.dossier_rejected import DossierRejected
from src.dossiers.domain.events.dossier_validated import DossierValidated
from src.shared.infrastructure.messaging.in_memory_event_bus import InMemoryEventBus


@pytest.mark.asyncio
async def test_validated_consumer_logs_event(caplog: pytest.LogCaptureFixture) -> None:
    """Vérifie que le consommateur de validation journalise les bonnes infos."""
    consumer = SendDossierValidatedEmailConsumer()
    dossier_id = uuid4()
    admin_id = uuid4()
    event = DossierValidated(
        dossier_id=dossier_id,
        admin_id=admin_id,
        comment="Dossier conforme",
    )

    with caplog.at_level(logging.INFO):
        await consumer.handle(event)

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert "DossierValidated" in record.message
    assert str(dossier_id) in record.message
    assert str(admin_id) in record.message
    assert "Dossier conforme" in record.message


@pytest.mark.asyncio
async def test_rejected_consumer_logs_event(caplog: pytest.LogCaptureFixture) -> None:
    """Vérifie que le consommateur de rejet journalise les bonnes infos."""
    consumer = SendDossierRejectedEmailConsumer()
    dossier_id = uuid4()
    admin_id = uuid4()
    event = DossierRejected(
        dossier_id=dossier_id,
        admin_id=admin_id,
        reason="Documents illisibles",
    )

    with caplog.at_level(logging.INFO):
        await consumer.handle(event)

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert "DossierRejected" in record.message
    assert str(dossier_id) in record.message
    assert "Documents illisibles" in record.message


@pytest.mark.asyncio
async def test_documents_requested_consumer_logs_event(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Vérifie que le consommateur de demande de documents journalise les bonnes infos."""
    consumer = SendDocumentsRequestedEmailConsumer()
    dossier_id = uuid4()
    admin_id = uuid4()
    event = DocumentsRequested(
        dossier_id=dossier_id,
        admin_id=admin_id,
        document_types=["IDENTITY_CARD", "PAYSLIP"],
    )

    with caplog.at_level(logging.INFO):
        await consumer.handle(event)

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert "DocumentsRequested" in record.message
    assert str(dossier_id) in record.message
    assert "IDENTITY_CARD" in record.message
    assert "PAYSLIP" in record.message


@pytest.mark.asyncio
async def test_consumer_called_via_event_bus() -> None:
    """Vérifie que le consommateur est appelé lors de la publication via l'EventBus."""
    bus = InMemoryEventBus()
    consumer = SendDossierValidatedEmailConsumer()
    bus.subscribe(DossierValidated, consumer.handle)

    event = DossierValidated(
        dossier_id=uuid4(),
        admin_id=uuid4(),
        comment="Test",
    )

    # Ne doit pas lever d'exception
    await bus.publish(event)
    assert bus.handler_count == 1


@pytest.mark.asyncio
async def test_failing_consumer_does_not_block_event_bus(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Vérifie qu'un consommateur en erreur n'empêche pas les autres de s'exécuter."""
    bus = InMemoryEventBus()

    async def failing_handler(event: DossierValidated) -> None:
        raise RuntimeError("Simulated failure")

    success_consumer = SendDossierValidatedEmailConsumer()

    bus.subscribe(DossierValidated, failing_handler)
    bus.subscribe(DossierValidated, success_consumer.handle)

    event = DossierValidated(
        dossier_id=uuid4(),
        admin_id=uuid4(),
        comment="Test résilience",
    )

    # L'EventBus doit attraper l'exception du premier handler
    # et continuer avec le second
    with caplog.at_level(logging.INFO):
        await bus.publish(event)

    # Le second handler a bien été exécuté malgré l'échec du premier
    info_messages = [r.message for r in caplog.records if r.levelno == logging.INFO]
    assert any("DossierValidated" in msg for msg in info_messages)
