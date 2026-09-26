from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from src.dossiers.domain.entities.document import Document
from src.dossiers.domain.entities.dossier import Dossier
from src.dossiers.domain.exceptions import (
    DocumentPendingPurgeNotAllowedException,
    DocumentPurgeNotAllowedException,
    InvalidDocumentStateException,
)
from src.dossiers.domain.value_objects.document_status import DocumentStatus
from src.dossiers.domain.value_objects.document_type import DocumentType
from src.dossiers.domain.value_objects.dossier_status import DossierStatus


def test_is_rejected_since_29_days_returns_false():
    now = datetime.now(timezone.utc)
    rejected_at = now - timedelta(days=29)
    dossier = Dossier(
        id=uuid4(),
        user_id=uuid4(),
        vehicle_id=uuid4(),
        status=DossierStatus.REJECTED,
        rejected_at=rejected_at,
    )
    assert dossier.is_rejected_since(30, reference_date=now) is False


def test_is_rejected_since_30_days_returns_true():
    now = datetime.now(timezone.utc)
    rejected_at = now - timedelta(days=30)
    dossier = Dossier(
        id=uuid4(),
        user_id=uuid4(),
        vehicle_id=uuid4(),
        status=DossierStatus.REJECTED,
        rejected_at=rejected_at,
    )
    assert dossier.is_rejected_since(30, reference_date=now) is True


def test_is_rejected_since_31_days_returns_true():
    now = datetime.now(timezone.utc)
    rejected_at = now - timedelta(days=31)
    dossier = Dossier(
        id=uuid4(),
        user_id=uuid4(),
        vehicle_id=uuid4(),
        status=DossierStatus.REJECTED,
        rejected_at=rejected_at,
    )
    assert dossier.is_rejected_since(30, reference_date=now) is True


def test_is_rejected_since_validated_status_returns_false():
    now = datetime.now(timezone.utc)
    rejected_at = now - timedelta(days=40)
    dossier = Dossier(
        id=uuid4(),
        user_id=uuid4(),
        vehicle_id=uuid4(),
        status=DossierStatus.VALIDATED,
        rejected_at=rejected_at,
    )
    assert dossier.is_rejected_since(30, reference_date=now) is False


def test_is_rejected_since_missing_rejected_at_returns_false():
    dossier = Dossier(
        id=uuid4(),
        user_id=uuid4(),
        vehicle_id=uuid4(),
        status=DossierStatus.REJECTED,
        rejected_at=None,
    )
    assert dossier.is_rejected_since(30) is False


@pytest.mark.parametrize(
    "status",
    [DocumentStatus.UPLOADED, DocumentStatus.VALIDATED, DocumentStatus.REJECTED],
)
def test_document_transition_to_pending_purge_allowed(status):
    doc = Document.create_pending(
        dossier_id=uuid4(),
        type=DocumentType.IDENTITY_CARD,
        s3_key="key",
        original_filename="id.pdf",
        content_type="application/pdf",
        size=1000,
    )
    doc.status = status
    doc.mark_as_pending_purge()
    assert doc.status == DocumentStatus.PENDING_PURGE


def test_document_pending_transition_to_pending_purge_refused():
    doc = Document.create_pending(
        dossier_id=uuid4(),
        type=DocumentType.IDENTITY_CARD,
        s3_key="key",
        original_filename="id.pdf",
        content_type="application/pdf",
        size=1000,
    )
    with pytest.raises(
        (DocumentPendingPurgeNotAllowedException, InvalidDocumentStateException)
    ):
        doc.mark_as_pending_purge()


def test_document_pending_purge_transition_to_purged_allowed():
    doc = Document.create_pending(
        dossier_id=uuid4(),
        type=DocumentType.IDENTITY_CARD,
        s3_key="key",
        original_filename="id.pdf",
        content_type="application/pdf",
        size=1000,
    )
    doc.status = DocumentStatus.PENDING_PURGE
    doc.mark_as_purged()
    assert doc.status == DocumentStatus.PURGED


def test_document_invalid_transition_to_purged_raises_exception():
    doc = Document.create_pending(
        dossier_id=uuid4(),
        type=DocumentType.IDENTITY_CARD,
        s3_key="key",
        original_filename="id.pdf",
        content_type="application/pdf",
        size=1000,
    )
    doc.status = DocumentStatus.UPLOADED
    with pytest.raises(
        (DocumentPurgeNotAllowedException, InvalidDocumentStateException)
    ):
        doc.mark_as_purged()
