"""Routes HTTP FastAPI pour l'API dossiers et gestion des pièces justificatives."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import get_current_user
from src.auth.domain.entities.user import User
from src.config import get_settings
from src.dossiers.application.commands.confirm_document_upload import (
    ConfirmDocumentUploadCommand,
    ConfirmDocumentUploadCommandHandler,
)
from src.dossiers.application.commands.cancel_dossier import (
    CancelDossierCommand,
    CancelDossierCommandHandler,
)
from src.dossiers.application.commands.create_dossier import (
    CreateDossierCommand,
    CreateDossierCommandHandler,
)
from src.dossiers.application.commands.submit_dossier import (
    SubmitDossierCommand,
    SubmitDossierCommandHandler,
)
from src.dossiers.application.schemas.dossier_schemas import (
    CreateDossierRequest,
    DossierResponse,
)
from src.dossiers.application.commands.request_document_upload import (
    RequestDocumentUploadCommand,
    RequestDocumentUploadCommandHandler,
)
from src.dossiers.application.services.authorization import can_access_document
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
from src.dossiers.domain.value_objects.financing_plan import FinancingPlan
from src.dossiers.domain.value_objects.trade_in import TradeIn
from src.dossiers.domain.exceptions import (
    DocumentNotFoundException,
    DossierAccessDeniedException,
    DossierNotFoundException,
    InvalidDocumentStateException,
    VehicleNotAvailableException,
    VehicleNotFoundException,
)
from src.dossiers.infrastructure.adapters.document_repository import (
    SqlAlchemyDocumentRepository,
)
from src.dossiers.infrastructure.dependencies import (
    get_cancel_dossier_handler,
    get_create_dossier_handler,
    get_submit_dossier_handler,
)

try:
    from src.dossiers.infrastructure.adapters.s3_document_storage import (
        S3DocumentStorageAdapter,
    )
except ImportError:
    # Fallback for environments without boto3
    S3DocumentStorageAdapter = None
from src.dossiers.infrastructure.repository.sqlalchemy_dossier_repository import (
    SQLAlchemyDossierRepository,
)
from src.shared.domain.exceptions import DomainError, NotFoundError
from src.shared.infrastructure.dependencies import SessionDep

from src.dossiers.application.schemas.document_schemas import ViewUrlResponse
from src.dossiers.application.schemas.dossier_response import (
    DossierListItemResponse,
    DossierStatusResponse,
)
from src.dossiers.domain.value_objects.dossier_status import DossierStatus

router = APIRouter(prefix="/api/v1/dossiers", tags=["dossiers"])


@router.post(
    "",
    response_model=DossierResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_dossier(
    request: CreateDossierRequest,
    current_user: User = Depends(get_current_user),
    handler: CreateDossierCommandHandler = Depends(get_create_dossier_handler),
) -> Dossier:
    """Crée un dossier brouillon pour un véhicule disponible."""
    trade_in = (
        TradeIn(
            registration=request.trade_in.registration,
            mileage=request.trade_in.mileage,
            brand=request.trade_in.brand,
            model=request.trade_in.model,
        )
        if request.trade_in is not None
        else None
    )
    financing_plan = (
        FinancingPlan(
            down_payment=request.financing_plan.down_payment,
            duration_months=request.financing_plan.duration_months,
            monthly_payment=request.financing_plan.monthly_payment,
        )
        if request.financing_plan is not None
        else None
    )
    try:
        return await handler.handle(
            CreateDossierCommand(
                user_id=current_user.id,
                vehicle_id=request.vehicle_id,
                trade_in=trade_in,
                financing_plan=financing_plan,
            )
        )
    except VehicleNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except VehicleNotAvailableException as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc


@router.get(
    "/me",
    response_model=list[DossierListItemResponse],
    status_code=status.HTTP_200_OK,
)
async def list_user_dossiers(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
) -> list[DossierListItemResponse]:
    """Récupère l'ensemble des dossiers appartenant à l'utilisateur connecté."""
    dossier_repo = SQLAlchemyDossierRepository(session)
    handler = ListUserDossiersQueryHandler(dossier_repository=dossier_repo)
    query = ListUserDossiersQuery(user_id=current_user.id)
    dossiers = await handler.handle(query)
    return [DossierListItemResponse.model_validate(dossier) for dossier in dossiers]


@router.get(
    "/{dossier_id}/status",
    response_model=DossierStatusResponse,
    status_code=status.HTTP_200_OK,
)
async def get_dossier_status(
    dossier_id: UUID,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
) -> DossierStatusResponse:
    """Récupère le statut d'un dossier avec contrôles d'accès anti-IDOR."""
    dossier_repo = SQLAlchemyDossierRepository(session)
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

    decision_comment = (
        dossier.rejection_reason
        if dossier.status == DossierStatus.REJECTED
        else dossier.comment
    )
    return DossierStatusResponse(
        status=dossier.status,
        updated_at=dossier.updated_at,
        decision_comment=decision_comment,
        requested_document_types=dossier.requested_document_types,
    )


@router.post(
    "/{dossier_id}/submit",
    response_model=DossierResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_dossier(
    dossier_id: UUID,
    current_user: User = Depends(get_current_user),
    handler: SubmitDossierCommandHandler = Depends(get_submit_dossier_handler),
) -> Dossier:
    """Soumet un dossier brouillon appartenant à l'utilisateur connecté."""
    try:
        return await handler.handle(
            SubmitDossierCommand(dossier_id=dossier_id, user_id=current_user.id)
        )
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except DossierAccessDeniedException as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
        ) from exc
    except DomainError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc


@router.post(
    "/{dossier_id}/cancel",
    response_model=DossierResponse,
    status_code=status.HTTP_200_OK,
)
async def cancel_dossier(
    dossier_id: UUID,
    current_user: User = Depends(get_current_user),
    handler: CancelDossierCommandHandler = Depends(get_cancel_dossier_handler),
) -> Dossier:
    """Annule un dossier brouillon appartenant à l'utilisateur connecté."""
    try:
        return await handler.handle(
            CancelDossierCommand(dossier_id=dossier_id, user_id=current_user.id)
        )
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except DossierAccessDeniedException as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
        ) from exc
    except DomainError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc


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
    if S3DocumentStorageAdapter is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service de stockage S3 non disponible (boto3 non installé)",
        )
    dossier_repo = SQLAlchemyDossierRepository(session)
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except DossierAccessDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e


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
    dossier_repo = SQLAlchemyDossierRepository(session)
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
    except (
        DossierNotFoundException,
        DocumentNotFoundException,
        InvalidDocumentStateException,
    ) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except DossierAccessDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e


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
    dossier_repo = SQLAlchemyDossierRepository(session)
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


@router.get(
    "/{dossier_id}/documents/{document_id}/view-url",
    response_model=ViewUrlResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Non authentifié (token absent/invalide)."},
        403: {"description": "Accès refusé (utilisateur non autorisé)."},
        404: {"description": "Dossier ou document introuvable."},
    },
    summary="Génère une URL pré-signée pour consulter un document.",
    description=(
        "Retourne une URL temporaire (60s) pour consulter un document. "
        "Nécessite une authentification et une autorisation valide."
    ),
)
async def get_document_view_url(
    dossier_id: UUID,
    document_id: UUID,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
) -> ViewUrlResponse:
    """Génère une URL pré-signée pour consulter un document (US-304).

    Contrôles:
    - 401 : Token absent/invalide (géré par get_current_user).
    - 404 : Dossier ou document introuvable (Critères 8,9).
    - 404 : Document non rattaché au dossier (Critère 9).
    - 403 : Utilisateur non autorisé (Critères 5,6).
    - 200 : URL pré-signée valide 60s (Critère 7).
    """
    if S3DocumentStorageAdapter is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service de stockage S3 non disponible (boto3 non installé)",
        )
    # Initialisation des dépendances
    dossier_repo = SQLAlchemyDossierRepository(session)
    document_repo = SqlAlchemyDocumentRepository(session)
    storage_adapter = S3DocumentStorageAdapter(get_settings())

    # 1. Récupération du dossier (Critère 8)
    dossier = await dossier_repo.get_by_id(dossier_id)
    if dossier is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dossier {dossier_id} introuvable.",
        )

    # 2. Récupération du document (Critère 8)
    document = await document_repo.find_by_id(document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} introuvable.",
        )

    # 3. Vérification que le document est rattaché au dossier (Critère 9)
    if document.dossier_id != dossier_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document non rattaché à ce dossier.",
        )

    # 4. Vérification des droits d'accès (Critères 3,4,5)
    if not can_access_document(current_user, document, dossier):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé : vous n'avez pas le droit de consulter ce document.",
        )

    # 5. Génération de l'URL pré-signée (Critère 7)
    url = await storage_adapter.generate_download_url(
        s3_key=document.s3_key,
        expires_in=60,
    )

    return ViewUrlResponse(url=url, expires_in=60)
