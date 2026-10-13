"""Module d'orchestration du planificateur de tâches asynchrones APScheduler."""

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from src.shared.infrastructure.config import Settings
from src.dossiers.application.use_cases.purge_rejected_dossiers import (
    PurgeRejectedDossiersUseCase,
)
from src.dossiers.infrastructure.adapters.s3_document_storage import (
    S3DocumentStorageAdapter,
)
from src.dossiers.infrastructure.adapters.document_repository import (
    SqlAlchemyDocumentRepository,
)
from src.dossiers.infrastructure.repository.sqlalchemy_dossier_repository import (
    SQLAlchemyDossierRepository,
)
from src.shared.infrastructure.database import get_session_factory
from src.shared.infrastructure.event_bus import EventBus
from src.shared.infrastructure.persistence.sqlalchemy_uow import SqlAlchemyUnitOfWork

logger = logging.getLogger(__name__)

JOB_ID_PURGE = "purge_rejected_dossiers"


async def run_purge_job() -> None:
    """Fonction d'orchestration instanciant les dépendances du cas d'usage de purge."""
    session_factory = get_session_factory()
    async with session_factory() as session:
        uow = SqlAlchemyUnitOfWork(session)
        dossier_repo = SQLAlchemyDossierRepository(session)
        document_repo = SqlAlchemyDocumentRepository(session)
        settings = Settings()
        storage = S3DocumentStorageAdapter(settings)
        event_bus = EventBus()

        use_case = PurgeRejectedDossiersUseCase(
            dossier_repository=dossier_repo,
            document_repository=document_repo,
            document_storage=storage,
            event_bus=event_bus,
            uow=uow,
        )
        await use_case.execute(days=30)


class ApplicationScheduler:
    """Gestionnaire de cycle de vie du planificateur APScheduler."""

    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler(timezone="UTC")

    def configure_jobs(self) -> None:
        """Enregistre le job quotidien s'il n'est pas déjà présent."""
        if not self.scheduler.get_job(JOB_ID_PURGE):
            self.scheduler.add_job(
                run_purge_job,
                trigger=CronTrigger(hour=3, minute=0, timezone="UTC"),
                id=JOB_ID_PURGE,
                replace_existing=True,
            )

    def start(self) -> None:
        self.configure_jobs()
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler démarré avec succès.")

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("Scheduler arrêté avec succès.")


app_scheduler = ApplicationScheduler()
