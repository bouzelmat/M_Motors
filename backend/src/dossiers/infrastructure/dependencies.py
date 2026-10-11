"""Dépendances FastAPI pour le module dossiers."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.infrastructure.dependencies import get_user_repository
from src.dossiers.application.commands.reject_dossier import (
    RejectDossierCommandHandler,
)
from src.dossiers.application.commands.cancel_dossier import (
    CancelDossierCommandHandler,
)
from src.dossiers.application.commands.create_dossier import (
    CreateDossierCommandHandler,
)
from src.dossiers.application.commands.request_documents import (
    RequestDocumentsCommandHandler,
)
from src.dossiers.application.commands.submit_dossier import (
    SubmitDossierCommandHandler,
)
from src.dossiers.application.commands.validate_dossier import (
    ValidateDossierCommandHandler,
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
from src.dossiers.domain.ports.document_repository import DocumentRepository
from src.dossiers.domain.ports.dossier_repository import DossierRepository
from src.dossiers.infrastructure.adapters.document_repository import (
    SqlAlchemyDocumentRepository,
)
from src.dossiers.infrastructure.repository.sqlalchemy_dossier_repository import (
    SQLAlchemyDossierRepository,
)
from src.shared.domain.ports.event_bus import AbstractEventBus
from src.shared.domain.ports.unit_of_work import AbstractUnitOfWork
from src.shared.infrastructure.database import get_session
from src.shared.infrastructure.messaging.in_memory_event_bus import get_event_bus
from src.shared.infrastructure.persistence.sqlalchemy_uow import SqlAlchemyUnitOfWork
from src.vehicles.infrastructure.dependencies import get_vehicle_repository


def get_dossier_repository(
    session: AsyncSession = Depends(get_session),
) -> DossierRepository:
    """Fournit une instance du dépôt de dossiers liée à la session courante."""
    return SQLAlchemyDossierRepository(session)


def get_document_repository(
    session: AsyncSession = Depends(get_session),
) -> DocumentRepository:
    """Fournit une instance du dépôt de documents liée à la session courante."""
    return SqlAlchemyDocumentRepository(session)


def get_uow(
    session: AsyncSession = Depends(get_session),
) -> AbstractUnitOfWork:
    """Fournit une instance d'Unit of Work liée à la session courante."""
    return SqlAlchemyUnitOfWork(session)


def get_event_bus_dependency() -> AbstractEventBus:
    """Fournit le singleton de l'Event Bus applicatif."""
    return get_event_bus()


def get_create_dossier_handler(
    dossier_repository: DossierRepository = Depends(get_dossier_repository),
    vehicle_repository=Depends(get_vehicle_repository),
    uow: AbstractUnitOfWork = Depends(get_uow),
    event_bus: AbstractEventBus = Depends(get_event_bus_dependency),
) -> CreateDossierCommandHandler:
    return CreateDossierCommandHandler(
        dossier_repository=dossier_repository,
        vehicle_repository=vehicle_repository,
        uow=uow,
        event_bus=event_bus,
    )


def get_submit_dossier_handler(
    dossier_repository: DossierRepository = Depends(get_dossier_repository),
    document_repository: DocumentRepository = Depends(get_document_repository),
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> SubmitDossierCommandHandler:
    return SubmitDossierCommandHandler(
        dossier_repository=dossier_repository,
        document_repository=document_repository,
        uow=uow,
    )


def get_cancel_dossier_handler(
    dossier_repository: DossierRepository = Depends(get_dossier_repository),
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> CancelDossierCommandHandler:
    """Fournit le handler d'annulation lié aux dépendances courantes."""
    return CancelDossierCommandHandler(
        dossier_repository=dossier_repository,
        uow=uow,
    )


def get_list_pending_dossiers_use_case(
    repository: DossierRepository = Depends(get_dossier_repository),
) -> ListPendingDossiersUseCase:
    """Fournit une instance du cas d'usage de consultation des dossiers en attente."""
    return ListPendingDossiersUseCase(dossier_repository=repository)


def get_list_dossier_history_use_case(
    repository: DossierRepository = Depends(get_dossier_repository),
) -> ListDossierHistoryUseCase:
    """Fournit le cas d'usage de consultation des dossiers clôturés."""
    return ListDossierHistoryUseCase(dossier_repository=repository)


def get_validate_dossier_handler(
    repository: DossierRepository = Depends(get_dossier_repository),
    uow: AbstractUnitOfWork = Depends(get_uow),
    event_bus: AbstractEventBus = Depends(get_event_bus_dependency),
) -> ValidateDossierCommandHandler:
    """Fournit une instance du handler de validation de dossier."""
    return ValidateDossierCommandHandler(
        dossier_repository=repository,
        uow=uow,
        event_bus=event_bus,
    )


def get_reject_dossier_handler(
    repository: DossierRepository = Depends(get_dossier_repository),
    uow: AbstractUnitOfWork = Depends(get_uow),
    event_bus: AbstractEventBus = Depends(get_event_bus_dependency),
) -> RejectDossierCommandHandler:
    """Fournit une instance du handler de rejet de dossier."""
    return RejectDossierCommandHandler(
        dossier_repository=repository,
        uow=uow,
        event_bus=event_bus,
    )


def get_request_documents_handler(
    repository: DossierRepository = Depends(get_dossier_repository),
    uow: AbstractUnitOfWork = Depends(get_uow),
    event_bus: AbstractEventBus = Depends(get_event_bus_dependency),
) -> RequestDocumentsCommandHandler:
    """Fournit une instance du handler de demande de documents complémentaires."""
    return RequestDocumentsCommandHandler(
        dossier_repository=repository,
        uow=uow,
        event_bus=event_bus,
    )


def get_admin_dossier_detail_use_case(
    dossier_repository: DossierRepository = Depends(get_dossier_repository),
    user_repository=Depends(get_user_repository),
    vehicle_repository=Depends(get_vehicle_repository),
    document_repository: DocumentRepository = Depends(get_document_repository),
) -> GetAdminDossierDetailUseCase:
    """Construit le use case de détail administrateur d'un dossier."""
    return GetAdminDossierDetailUseCase(
        dossier_repository=dossier_repository,
        user_repository=user_repository,
        vehicle_repository=vehicle_repository,
        document_repository=document_repository,
    )
