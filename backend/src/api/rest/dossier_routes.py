"""Routes HTTP FastAPI pour l'API dossiers et gestion des pièces justificatives."""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import get_current_user
from src.auth.domain.entities.user import User
from src.config import get_settings
from src.dossiers.application.commands.confirm_document_upload import (
    ConfirmDocumentUploadCommand,
    ConfirmDocumentUploadCommandHandler,
)
from src.dossiers.application.commands.request_document_upload import (
    RequestDocumentUploadCommand,
    RequestDocumentUploadCommandHandler,
)
from src.dossiers.application.queries.get_dossier_status import (
    GetDossierStatusQuery,
    GetDossierStatusQueryHandler,
)
from src.dossiers.application.queries.list_user_dossiers import (
    ListUserDossiersQuery,
    ListUserDossiersQueryHandler,
)
from src.dossiers.application.schemas.document_schemas import (
    DocumentConfirmResponse,
    DocumentListItemResponse,
    PresignedUrlRequest,
    PresignedUrlResponse,
)
from src.dossiers.domain.entities.dossier import Dossier
from src.dossiers.domain.exceptions import (
    DocumentNotFoundException,
    DossierAccessDeniedException,
    DossierNotFoundException,
    InvalidDocumentStateException,
)
from src.dossiers.infrastructure.adapters.document_repository import (
    SqlAlchemyDocumentRepository,
)
from src.dossiers.infrastructure.adapters.s3_document_storage import (
    S3DocumentStorageAdapter,
)
from src.dossiers.infrastructure.persistence.dossier_repository import (
    SqlAlchemyDossierRepository,
)
from src.shared.infrastructure.dependencies import SessionDep

router = APIRouter(prefix="/api/v1/dossiers", tags=["dossiers"])


@router.get(
    "/me",
    response_model=list[Dossier],
    status_code=status.HTTP_200_OK,
)
async def list_user_dossiers(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
) -> list[Dossier]:
    """Récupère l'ensemble des dossiers appartenant à l'utilisateur connecté."""
    dossier_repo = SqlAlchemyDossierRepository(session)
    handler = ListUserDossiersQueryHandler(dossier_repository=dossier_repo)
    query = ListUserDossiersQuery(user_id=current_user.id)
    return await handler.handle(query)


@router.get(
    "/{dossier_id}/status",
    status_code=status.HTTP_200_OK,
)
async def get_dossier_status(
    dossier_id: UUID,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Récupère le statut d'un dossier avec contrôles d'accès anti-IDOR."""
    dossier_repo = SqlAlchemyDossierRepository(session)
    handler = GetDossierStatusQueryHandler(dossier_repository=dossier_repo)

    dossier = await handler.handle(GetDossierStatusQuery(dossier_id=dossier_id))

    if dossier is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dossier {dossier_id} introuvable.",
        )

    if dossier.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé : vous n'êtes pas propriétaire de ce dossier.",
        )

    return {
        "status": dossier.status,
        "updated_at": dossier.updated_at.isoformat(),
        "decision_comment": getattr(dossier, "decision_comment", None),
    }


@router.post(
    "/{dossier_id}/documents/presigned-url",
    response_model=PresignedUrlResponse,
    status_code=status.HTTP_200_OK,
)
async def request_presigned_url(
    dossier_id: UUID,
    request: PresignedUrlRequest,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
) -> PresignedUrlResponse:
    """Génère une URL pré-signée S3 pour le téléversement d'un document."""
    dossier_repo = SqlAlchemyDossierRepository(session)
    document_repo = SqlAlchemyDocumentRepository(session)
    storage_adapter = S3DocumentStorageAdapter(get_settings())

    handler = RequestDocumentUploadCommandHandler(
        dossier_repository=dossier_repo,
        document_repository=document_repo,
        storage_port=storage_adapter,
    )

    command = RequestDocumentUploadCommand(
        dossier_id=dossier_id,
        user_id=current_user.id,
        document_type=request.document_type,
        filename=request.filename,
        content_type=request.content_type,
        size=request.size,
    )

    try:
        result = await handler.handle(command)
        await session.commit()
        return PresignedUrlResponse(
            document_id=result.document.id,
            upload_url=result.upload_url,
            s3_key=result.document.s3_key,
        )
    except DossierNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DossierAccessDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/{dossier_id}/documents/{document_id}/confirm",
    response_model=DocumentConfirmResponse,
    status_code=status.HTTP_200_OK,
)
async def confirm_document_upload(
    dossier_id: UUID,
    document_id: UUID,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
) -> DocumentConfirmResponse:
    """Confirms le téléversement effectif d'un document sur S3."""
    dossier_repo = SqlAlchemyDossierRepository(session)
    document_repo = SqlAlchemyDocumentRepository(session)

    handler = ConfirmDocumentUploadCommandHandler(
        dossier_repository=dossier_repo,
        document_repository=document_repo,
    )

    command = ConfirmDocumentUploadCommand(
        dossier_id=dossier_id,
        document_id=document_id,
        user_id=current_user.id,
    )

    try:
        document = await handler.handle(command)
        await session.commit()
        return DocumentConfirmResponse.model_validate(document)
    except (DossierNotFoundException, DocumentNotFoundException, InvalidDocumentStateException) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DossierAccessDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get(
    "/{dossier_id}/documents",
    response_model=list[DocumentListItemResponse],
    status_code=status.HTTP_200_OK,
)
async def list_documents(
    dossier_id: UUID,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
) -> list[DocumentListItemResponse]:
    """Récupère l'ensemble des documents associés à un dossier."""
    dossier_repo = SqlAlchemyDossierRepository(session)
    document_repo = SqlAlchemyDocumentRepository(session)

    dossier = await dossier_repo.get_by_id(dossier_id)
    if dossier is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dossier {dossier_id} introuvable.",
        )

    if dossier.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé : vous n'êtes pas propriétaire de ce dossier.",
        )

    documents = await document_repo.find_by_dossier(dossier_id)
    return [DocumentListItemResponse.model_validate(doc) for doc in documents]