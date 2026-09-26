"""Cas d'utilisation pour la purge automatisée des documents S3 des dossiers rejetés."""

from dataclasses import asdict, dataclass
import json
import logging

from src.dossiers.domain.events.dossier_purged import DossierPurged
from src.dossiers.domain.ports.document_repository import DocumentRepository
from src.dossiers.domain.ports.document_storage_port import DocumentStoragePort
from src.dossiers.domain.ports.dossier_repository import DossierRepository
from src.dossiers.domain.value_objects.document_status import DocumentStatus
from src.shared.domain.ports.event_bus import AbstractEventBus
from src.shared.domain.ports.unit_of_work import AbstractUnitOfWork

logger = logging.getLogger(__name__)


@dataclass
class PurgeReport:
    """Rapport d'exécution de la tâche de purge."""

    dossiers_traites: int = 0
    documents_purges: int = 0
    erreurs: int = 0


class PurgeRejectedDossiersUseCase:
    """Cas d'usage exécutant la purge à deux phases (DB/S3/DB) des documents rejetés."""

    def __init__(
        self,
        dossier_repository: DossierRepository,
        document_repository: DocumentRepository,
        document_storage: DocumentStoragePort,
        event_bus: AbstractEventBus,
        uow: AbstractUnitOfWork,
    ) -> None:
        self._dossier_repo = dossier_repository
        self._document_repo = document_repository
        self._storage = document_storage
        self._event_bus = event_bus
        self._uow = uow

    async def execute(self, days: int = 30) -> PurgeReport:
        report = PurgeReport()
        dossiers = await self._dossier_repo.find_rejected_since(days=days)

        for dossier in dossiers:
            report.dossiers_traites += 1
            documents = await self._document_repo.find_by_dossier(dossier.id)

            all_documents_purged = True

            for doc in documents:
                # 1. Ignorer PENDING + warning log
                if doc.status == DocumentStatus.PENDING:
                    logger.warning(
                        "Document %s pour dossier %s au statut PENDING ignoré lors de la purge",
                        doc.id,
                        dossier.id,
                    )
                    all_documents_purged = False
                    continue

                # 2. Ignorer déjà PURGED
                if doc.status == DocumentStatus.PURGED:
                    continue

                # 3. Transition phase 1 DB (si pas déjà PENDING_PURGE)
                if doc.status != DocumentStatus.PENDING_PURGE:
                    async with self._uow:
                        doc.mark_as_pending_purge()
                        await self._document_repo.save(doc)
                        await self._uow.commit()

                # 4. Suppression physique S3 (HORS TRANSACTION DB)
                try:
                    await self._storage.delete_object(doc.s3_key)
                except Exception as exc:  # noqa: BLE001
                    logger.error(
                        "Échec de la suppression S3 pour le document %s (clé %s) : %s",
                        doc.id,
                        doc.s3_key,
                        exc,
                    )
                    report.erreurs += 1
                    all_documents_purged = False
                    continue

                # 5. Transition phase 2 DB (après succès S3)
                async with self._uow:
                    doc.mark_as_purged()
                    await self._document_repo.save(doc)
                    await self._uow.commit()

                report.documents_purges += 1

            # 6. Émettre l'événement domaine si TOUS les documents sont purgés
            if all_documents_purged and documents:
                await self._event_bus.publish(DossierPurged(dossier_id=dossier.id))

        # Log de fin au format JSON
        logger.info(
            json.dumps(
                {
                    "event": "purge_completed",
                    **asdict(report),
                }
            )
        )

        return report
