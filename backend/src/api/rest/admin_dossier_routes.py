"""Routes API d'administration pour la gestion et validation des dossiers."""

from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.dependencies import require_admin
from src.auth.domain.entities.user import User
from src.dossiers.application.commands.reject_dossier import (
    RejectDossierCommand,
    RejectDossierCommandHandler,
)
from src.dossiers.application.commands.request_documents import (
    RequestDocumentsCommand,
    RequestDocumentsCommandHandler,
)
from src.dossiers.application.commands.validate_dossier import (
    ValidateDossierCommand,
    ValidateDossierCommandHandler,
)
from src.dossiers.application.queries.get_admin_dossier_detail import (
    GetAdminDossierDetailQuery,
)
from src.dossiers.application.queries.list_pending_dossiers import (
    ListPendingDossiersQuery,
)
from src.dossiers.application.queries.list_dossier_history import (
    ListDossierHistoryQuery,
)
from src.dossiers.application.schemas.dossier_response import (
    AdminDossierDetailResponse,
    PendingDossierResponse,
)
from src.dossiers.application.schemas.dossier_schemas import (
    RejectDossierRequest,
    RequestDocumentsRequest,
    ValidateDossierRequest,
)
from src.dossiers.application.use_cases.get_admin_dossier_detail import (
    GetAdminDossierDetailUseCase,
)
from src.dossiers.application.use_cases.list_pending_dossiers import (
    ListPendingDossiersUseCase,
)
from src.dossiers.application.use_cases.list_dossier_history import (
    ListDossierHistoryUseCase,
)
from src.dossiers.infrastructure.dependencies import (
    get_admin_dossier_detail_use_case,
    get_list_pending_dossiers_use_case,
    get_list_dossier_history_use_case,
    get_reject_dossier_handler,
    get_request_documents_handler,
    get_validate_dossier_handler,
)
from src.shared.domain.exceptions import DomainError, NotFoundError

router = APIRouter(prefix="/admin/dossiers", tags=["Admin Dossiers"])


@router.get(
    "/pending",
    response_model=list[PendingDossierResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin)],
)
async def get_pending_dossiers(
    sort_by: Annotated[
        Literal["submitted_at", "created_at", "updated_at"],
        Query(description="Champ d'horodatage utilisé pour le tri décroissant"),
    ] = "submitted_at",
    use_case: ListPendingDossiersUseCase = Depends(get_list_pending_dossiers_use_case),
) -> list[PendingDossierResponse]:
    """Récupère la liste de tous les dossiers en attente de traitement."""
    query = ListPendingDossiersQuery(sort_by=sort_by)
    try:
        results = await use_case.execute(query)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid request",
        ) from e
    return [PendingDossierResponse.model_validate(r) for r in results]


@router.get(
    "/history",
    response_model=list[PendingDossierResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin)],
)
async def get_dossier_history(
    use_case: ListDossierHistoryUseCase = Depends(get_list_dossier_history_use_case),
) -> list[PendingDossierResponse]:
    """Récupère les dossiers clôturés pour consultation par les administrateurs."""
    results = await use_case.execute(ListDossierHistoryQuery())
    return [PendingDossierResponse.model_validate(result) for result in results]


@router.get(
    "/{dossier_id}",
    response_model=AdminDossierDetailResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin)],
)
async def get_dossier_detail(
    dossier_id: UUID,
    use_case: GetAdminDossierDetailUseCase = Depends(get_admin_dossier_detail_use_case),
) -> AdminDossierDetailResponse:
    """Récupère le détail complet d'un dossier pour le back-office."""
    try:
        query = GetAdminDossierDetailQuery(dossier_id=dossier_id)
        read_model = await use_case.execute(query)
        return AdminDossierDetailResponse.model_validate(read_model)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        ) from exc


@router.post(
    "/{dossier_id}/validate",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin)],
)
async def validate_dossier(
    dossier_id: UUID,
    payload: ValidateDossierRequest,
    current_user: Annotated[User, Depends(require_admin)],
    handler: ValidateDossierCommandHandler = Depends(get_validate_dossier_handler),
) -> dict[str, str]:
    """Valide un dossier soumis."""
    try:
        command = ValidateDossierCommand(
            dossier_id=dossier_id,
            admin_id=current_user.id,
            comment=payload.comment,
        )
        dossier = await handler.handle(command)
        return {
            "message": "Dossier validé avec succès.",
            "dossier_id": str(dossier.id),
            "status": dossier.status.value,
        }
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        ) from exc
    except DomainError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflict",
        ) from exc


@router.post(
    "/{dossier_id}/reject",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin)],
)
async def reject_dossier(
    dossier_id: UUID,
    payload: RejectDossierRequest,
    current_user: Annotated[User, Depends(require_admin)],
    handler: RejectDossierCommandHandler = Depends(get_reject_dossier_handler),
) -> dict[str, str]:
    """Rejette un dossier soumis avec un motif obligatoire."""
    try:
        command = RejectDossierCommand(
            dossier_id=dossier_id,
            admin_id=current_user.id,
            reason=payload.reason,
        )
        dossier = await handler.handle(command)
        return {
            "message": "Dossier rejeté.",
            "dossier_id": str(dossier.id),
            "status": dossier.status.value,
        }
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        ) from exc
    except DomainError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflict",
        ) from exc


@router.post(
    "/{dossier_id}/request-documents",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin)],
)
async def request_documents(
    dossier_id: UUID,
    payload: RequestDocumentsRequest,
    current_user: Annotated[User, Depends(require_admin)],
    handler: RequestDocumentsCommandHandler = Depends(get_request_documents_handler),
) -> dict[str, str]:
    """Demande des documents complémentaires pour un dossier."""
    try:
        command = RequestDocumentsCommand(
            dossier_id=dossier_id,
            admin_id=current_user.id,
            document_types=[dt.value for dt in payload.document_types],
        )
        dossier = await handler.handle(command)
        return {
            "message": "Demande de documents envoyée.",
            "dossier_id": str(dossier.id),
            "status": dossier.status.value,
        }
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        ) from exc
    except DomainError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflict",
        ) from exc
