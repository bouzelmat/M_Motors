from uuid import uuid4

import pytest

from src.dossiers.application.commands.submit_dossier import (
    SubmitDossierCommand,
    SubmitDossierCommandHandler,
)
from src.dossiers.domain.entities.document import Document
from src.dossiers.domain.entities.dossier import Dossier
from src.dossiers.domain.exceptions import DossierAccessDeniedException
from src.dossiers.domain.value_objects.document_status import DocumentStatus
from src.dossiers.domain.value_objects.document_type import DocumentType
from src.dossiers.domain.value_objects.dossier_status import DossierStatus
from src.shared.domain.exceptions import DomainError


class FakeDossierRepository:
    def __init__(self, dossier: Dossier) -> None:
        self.dossier = dossier
        self.saved: Dossier | None = None

    async def get_by_id_for_update(self, dossier_id):
        return self.dossier if dossier_id == self.dossier.id else None

    async def save(self, dossier: Dossier) -> None:
        self.saved = dossier


class FakeDocumentRepository:
    def __init__(self, documents: list[Document]) -> None:
        self.documents = documents

    async def find_by_dossier(self, dossier_id):
        return self.documents


class FakeUnitOfWork:
    def __init__(self) -> None:
        self.committed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return None

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        return None


def uploaded_document(dossier_id, document_type=DocumentType.IDENTITY_CARD):
    return Document(
        id=uuid4(),
        dossier_id=dossier_id,
        type=document_type,
        s3_key="test/document.pdf",
        status=DocumentStatus.UPLOADED,
        original_filename="document.pdf",
        content_type="application/pdf",
        size=100,
        created_at=Dossier.create(user_id=uuid4(), vehicle_id=uuid4()).created_at,
    )


@pytest.mark.asyncio
async def test_submit_requires_uploaded_document() -> None:
    dossier = Dossier.create(user_id=uuid4(), vehicle_id=uuid4())
    uow = FakeUnitOfWork()
    handler = SubmitDossierCommandHandler(
        FakeDossierRepository(dossier), FakeDocumentRepository([]), uow
    )

    with pytest.raises(DomainError, match="justificatif téléversé"):
        await handler.handle(
            SubmitDossierCommand(dossier_id=dossier.id, user_id=dossier.user_id)
        )

    assert uow.committed is False


@pytest.mark.asyncio
async def test_submit_does_not_accept_pending_document() -> None:
    dossier = Dossier.create(user_id=uuid4(), vehicle_id=uuid4())
    document = uploaded_document(dossier.id)
    document.status = DocumentStatus.PENDING
    handler = SubmitDossierCommandHandler(
        FakeDossierRepository(dossier),
        FakeDocumentRepository([document]),
        FakeUnitOfWork(),
    )

    with pytest.raises(DomainError, match="justificatif téléversé"):
        await handler.handle(
            SubmitDossierCommand(dossier_id=dossier.id, user_id=dossier.user_id)
        )


@pytest.mark.asyncio
async def test_submit_requires_all_requested_document_types() -> None:
    dossier = Dossier.create(user_id=uuid4(), vehicle_id=uuid4()).submit()
    dossier = dossier.request_documents(["IDENTITY_CARD", "PROOF_OF_ADDRESS"])
    handler = SubmitDossierCommandHandler(
        FakeDossierRepository(dossier),
        FakeDocumentRepository([uploaded_document(dossier.id)]),
        FakeUnitOfWork(),
    )

    with pytest.raises(DomainError, match="tous les documents demandés"):
        await handler.handle(
            SubmitDossierCommand(dossier_id=dossier.id, user_id=dossier.user_id)
        )


@pytest.mark.asyncio
async def test_submit_rejects_non_owner() -> None:
    dossier = Dossier.create(user_id=uuid4(), vehicle_id=uuid4())
    handler = SubmitDossierCommandHandler(
        FakeDossierRepository(dossier),
        FakeDocumentRepository([uploaded_document(dossier.id)]),
        FakeUnitOfWork(),
    )

    with pytest.raises(DossierAccessDeniedException):
        await handler.handle(SubmitDossierCommand(dossier.id, uuid4()))


@pytest.mark.asyncio
async def test_submit_commits_dossier_with_uploaded_document() -> None:
    dossier = Dossier.create(user_id=uuid4(), vehicle_id=uuid4())
    repository = FakeDossierRepository(dossier)
    uow = FakeUnitOfWork()
    handler = SubmitDossierCommandHandler(
        repository, FakeDocumentRepository([uploaded_document(dossier.id)]), uow
    )

    result = await handler.handle(
        SubmitDossierCommand(dossier_id=dossier.id, user_id=dossier.user_id)
    )

    assert result.status == DossierStatus.SUBMITTED
    assert repository.saved == result
    assert uow.committed is True
