"""Tests unitaires pour DocumentMapper."""

from datetime import datetime, timezone
from uuid import uuid4

from src.dossiers.domain.entities.document import Document
from src.dossiers.domain.value_objects.document_status import DocumentStatus
from src.dossiers.domain.value_objects.document_type import DocumentType
from src.dossiers.infrastructure.models.document_model import DocumentModel
from src.dossiers.infrastructure.mapper.document_mapper import DocumentMapper


def test_mapper_to_domain_preserves_none_uploaded_at() -> None:
    doc_id = uuid4()
    dossier_id = uuid4()
    now = datetime.now(timezone.utc)

    model = DocumentModel(
        id=doc_id,
        dossier_id=dossier_id,
        type=DocumentType.IDENTITY_CARD,
        s3_key="dossiers/123/cni.pdf",
        status=DocumentStatus.PENDING,
        original_filename="cni.pdf",
        content_type="application/pdf",
        size=1024,
        created_at=now,
        uploaded_at=None,
    )

    entity = DocumentMapper.to_domain(model)

    assert entity.id == doc_id
    assert entity.dossier_id == dossier_id
    assert entity.type == DocumentType.IDENTITY_CARD
    assert entity.status == DocumentStatus.PENDING
    assert entity.uploaded_at is None
    assert entity.created_at == now


def test_mapper_to_model_preserves_all_attributes() -> None:
    doc_id = uuid4()
    dossier_id = uuid4()
    now = datetime.now(timezone.utc)

    entity = Document(
        id=doc_id,
        dossier_id=dossier_id,
        type=DocumentType.PAYSLIP,
        s3_key="dossiers/123/pay.pdf",
        status=DocumentStatus.UPLOADED,
        original_filename="pay.pdf",
        content_type="application/pdf",
        size=2048,
        created_at=now,
        uploaded_at=now,
    )

    model = DocumentMapper.to_model(entity)

    assert model.id == doc_id
    assert model.dossier_id == dossier_id
    assert model.type == DocumentType.PAYSLIP
    assert model.status == DocumentStatus.UPLOADED
    assert model.uploaded_at == now
