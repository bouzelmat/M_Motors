from unittest.mock import AsyncMock, MagicMock

import pytest

from src.dossiers.application.use_cases.purge_rejected_dossiers import (
    PurgeRejectedDossiersUseCase,
)
from src.dossiers.domain.events.dossier_purged import DossierPurged
from src.dossiers.domain.value_objects.document_status import DocumentStatus


@pytest.fixture
def mock_dependencies():
    return {
        "dossier_repository": AsyncMock(),
        "document_repository": AsyncMock(),
        "document_storage": AsyncMock(),
        "event_bus": AsyncMock(),
        "uow": AsyncMock(),
    }


def create_mock_doc(doc_id, status, s3_key="key/path"):
    doc = MagicMock()
    doc.id = doc_id
    doc.status = status
    doc.s3_key = s3_key
    return doc


@pytest.mark.asyncio
async def test_purge_two_uploaded_documents_success(mock_dependencies):
    dossier = MagicMock(id="dossier-1")
    doc1 = create_mock_doc("doc-1", DocumentStatus.UPLOADED, "key-1")
    doc2 = create_mock_doc("doc-2", DocumentStatus.VALIDATED, "key-2")

    mock_dependencies["dossier_repository"].find_rejected_since.return_value = [dossier]
    mock_dependencies["document_repository"].find_by_dossier.return_value = [doc1, doc2]

    use_case = PurgeRejectedDossiersUseCase(**mock_dependencies)
    report = await use_case.execute(30)

    assert report.dossiers_traites == 1
    assert report.documents_purges == 2
    assert report.erreurs == 0

    assert mock_dependencies["document_storage"].delete_object.call_count == 2
    assert doc1.mark_as_pending_purge.called
    assert doc1.mark_as_purged.called
    assert doc2.mark_as_pending_purge.called
    assert doc2.mark_as_purged.called

    # Vérification publication événement
    mock_dependencies["event_bus"].publish.assert_called_once()
    published_event = mock_dependencies["event_bus"].publish.call_args[0][0]
    assert isinstance(published_event, DossierPurged)
    assert published_event.dossier_id == "dossier-1"


@pytest.mark.asyncio
async def test_purge_pending_and_purged_documents_ignored(mock_dependencies, caplog):
    dossier = MagicMock(id="dossier-1")
    doc_pending = create_mock_doc("doc-pending", DocumentStatus.PENDING)
    doc_purged = create_mock_doc("doc-purged", DocumentStatus.PURGED)

    mock_dependencies["dossier_repository"].find_rejected_since.return_value = [dossier]
    mock_dependencies["document_repository"].find_by_dossier.return_value = [
        doc_pending,
        doc_purged,
    ]

    use_case = PurgeRejectedDossiersUseCase(**mock_dependencies)
    report = await use_case.execute(30)

    assert report.documents_purges == 0
    mock_dependencies["document_storage"].delete_object.assert_not_called()
    assert "PENDING ignoré" in caplog.text


@pytest.mark.asyncio
async def test_purge_pending_purge_resumes_s3_deletion(mock_dependencies):
    dossier = MagicMock(id="dossier-1")
    doc = create_mock_doc("doc-1", DocumentStatus.PENDING_PURGE, "key-1")

    mock_dependencies["dossier_repository"].find_rejected_since.return_value = [dossier]
    mock_dependencies["document_repository"].find_by_dossier.return_value = [doc]

    use_case = PurgeRejectedDossiersUseCase(**mock_dependencies)
    await use_case.execute(30)

    doc.mark_as_pending_purge.assert_not_called()
    mock_dependencies["document_storage"].delete_object.assert_called_once_with("key-1")
    doc.mark_as_purged.assert_called_once()


@pytest.mark.asyncio
async def test_s3_failure_increments_errors_and_continues(mock_dependencies):
    dossier = MagicMock(id="dossier-1")
    doc1 = create_mock_doc("doc-1", DocumentStatus.UPLOADED, "key-1")
    doc2 = create_mock_doc("doc-2", DocumentStatus.UPLOADED, "key-2")

    mock_dependencies["dossier_repository"].find_rejected_since.return_value = [dossier]
    mock_dependencies["document_repository"].find_by_dossier.return_value = [doc1, doc2]

    # Simuler échec sur premier doc
    mock_dependencies["document_storage"].delete_object.side_effect = [
        Exception("S3 Down"),
        None,
    ]

    use_case = PurgeRejectedDossiersUseCase(**mock_dependencies)
    report = await use_case.execute(30)

    assert report.erreurs == 1
    assert report.documents_purges == 1
    doc1.mark_as_purged.assert_not_called()
    doc2.mark_as_purged.assert_called_once()
    mock_dependencies["event_bus"].publish.assert_not_called()
