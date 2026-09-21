"""Domain unit tests for Document entity."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from src.dossiers.domain.entities.document import Document
from src.dossiers.domain.value_objects.document_status import DocumentStatus
from src.dossiers.domain.value_objects.document_type import DocumentType
from src.shared.domain.exceptions import DomainError


def test_create_pending_document() -> None:
    dossier_id = uuid4()
    doc = Document.create_pending(
        dossier_id=dossier_id,
        type=DocumentType.IDENTITY_CARD,
        s3_key="dossiers/123/cni.pdf",
        original_filename="cni.pdf",
        content_type="application/pdf",
        size=1024,
    )

    assert doc.dossier_id == dossier_id
    assert doc.type == DocumentType.IDENTITY_CARD
    assert doc.s3_key == "dossiers/123/cni.pdf"
    assert doc.status == DocumentStatus.PENDING
    assert doc.uploaded_at is None
    assert doc.created_at.tzinfo == timezone.utc


def test_mark_as_uploaded_success() -> None:
    doc = Document.create_pending(
        dossier_id=uuid4(),
        type=DocumentType.PROOF_OF_ADDRESS,
        s3_key="dossiers/123/justif.pdf",
        original_filename="justif.pdf",
        content_type="application/pdf",
        size=2048,
    )

    now = datetime.now(timezone.utc)
    doc.mark_as_uploaded(now=now)

    assert doc.status == DocumentStatus.UPLOADED
    assert doc.uploaded_at == now


def test_mark_as_uploaded_twice_raises_domain_error() -> None:
    doc = Document.create_pending(
        dossier_id=uuid4(),
        type=DocumentType.PAYSLIP,
        s3_key="dossiers/123/bulletin.pdf",
        original_filename="bulletin.pdf",
        content_type="application/pdf",
        size=4096,
    )

    doc.mark_as_uploaded()

    with pytest.raises(DomainError, match="Impossible de marquer comme téléversé"):
        doc.mark_as_uploaded()


def test_mark_as_uploaded_from_validated_raises_domain_error() -> None:
    doc = Document(
        id=uuid4(),
        dossier_id=uuid4(),
        type=DocumentType.BANK_DETAILS,
        s3_key="dossiers/123/rib.pdf",
        status=DocumentStatus.VALIDATED,
        original_filename="rib.pdf",
        content_type="application/pdf",
        size=512,
        created_at=datetime.now(timezone.utc),
        uploaded_at=datetime.now(timezone.utc),
    )

    with pytest.raises(DomainError, match="Impossible de marquer comme téléversé"):
        doc.mark_as_uploaded()
