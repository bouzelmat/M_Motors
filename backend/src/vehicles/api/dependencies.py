"""Dépendances FastAPI et câblage de l'injection pour le contexte vehicles."""

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.infrastructure.database import get_session
from src.vehicles.application.commands.toggle_vehicle_type import (
    ToggleVehicleTypeCommandHandler,
)
from src.vehicles.domain.ports.dossier_existence_port import DossierExistencePort


# --- FEATURE FLAG (Inhibe la route en prod tant que Tâche 3 n'est pas livrée) ---
class Settings:
    ENABLE_TOGGLE_CATALOG_TYPE: bool = False  # Passer à True une fois la Tâche 3 livrée


settings = Settings()


async def check_toggle_feature_enabled() -> None:
    """Guard HTTP bloquant l'accès à l'endpoint si la fonctionnalité est désactivée."""
    if not settings.ENABLE_TOGGLE_CATALOG_TYPE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cette fonctionnalité est temporairement désactivée (en attente de l'adaptateur de dossiers).",
        )


# --- AUTHENTIFICATION ADMIN (Réutilisation du contrat existant) ---
async def get_current_admin_user() -> dict:
    """Mock de la dépendance d'autorisation Admin déjà existante dans l'application."""
    # En environnement réel, cette méthode extrait et vérifie le JWT de l'admin
    return {"sub": "admin_user_id", "role": "admin"}


# --- PROVIDERS D'INJECTEUR ---
async def get_dossier_existence_port_stub() -> DossierExistencePort:
    """Port temporaire / Fake tant que la Tâche 3 n'est pas terminée.

    ATTENTION : Ne pas déployer en production avec cette implémentation stub !
    """

    class TemporaryDossierExistenceAdapter(DossierExistencePort):
        async def has_active_dossier_for_vehicle(self, vehicle_id) -> bool:
            return False

    return TemporaryDossierExistenceAdapter()


async def get_toggle_vehicle_type_handler(
    session: AsyncSession = Depends(get_session),
    dossier_port: DossierExistencePort = Depends(get_dossier_existence_port_stub),
) -> ToggleVehicleTypeCommandHandler:
    """Fabrique du command handler injectant les repositories, UoW, EventBus et le Port."""
    # Remarque : Remplacer les fakes/stubs par les vraies instances déclarées dans l'App
    from src.shared.infrastructure.messaging.in_memory_event_bus import InMemoryEventBus
    from src.shared.infrastructure.persistence.sqlalchemy_uow import (
        SqlAlchemyUnitOfWork,
    )
    from src.vehicles.infrastructure.repositories.sqlalchemy_vehicle_repository import (
        SQLAlchemyVehicleRepository,
    )

    repo = SQLAlchemyVehicleRepository(session)
    uow = SqlAlchemyUnitOfWork(session)
    bus = InMemoryEventBus()

    return ToggleVehicleTypeCommandHandler(
        repository=repo,
        uow=uow,
        event_bus=bus,
        dossier_existence_port=dossier_port,
    )
