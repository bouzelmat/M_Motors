"""Command et Command Handler pour l'expiration des dossiers DRAFT hors délai."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from src.dossiers.domain.constants import DRAFT_UPLOAD_TIMEOUT_MINUTES
from src.dossiers.domain.events.dossier_expired import DossierExpired
from src.dossiers.domain.ports.dossier_repository import DossierRepository
from src.shared.domain.ports.event_bus import AbstractEventBus
from src.shared.domain.ports.unit_of_work import AbstractUnitOfWork


@dataclass(frozen=True)
class ExpireStaleDossiersCommand:
    """Commande exécutée périodiquement pour expirer les dossiers DRAFT hors délai."""

    now: datetime | None = None


class ExpireStaleDossiersCommandHandler:
    """Fait transiter vers EXPIRED tout dossier DRAFT dont le début d'upload dépasse le délai imparti."""

    def __init__(
        self,
        repository: DossierRepository,
        uow: AbstractUnitOfWork,
        event_bus: AbstractEventBus,
    ) -> None:
        self._repository = repository
        self._uow = uow
        self._event_bus = event_bus

    async def handle(self, command: ExpireStaleDossiersCommand) -> int:
        """Exécute l'expiration des dossiers obsolètes sous verrouillage transactionnel."""
        execution_time = command.now or datetime.now(timezone.utc)
        cutoff_time = execution_time - timedelta(minutes=DRAFT_UPLOAD_TIMEOUT_MINUTES)

        async with self._uow:
            # La lecture s'effectue dans la transaction pour exploiter le SELECT ... FOR UPDATE SKIP LOCKED
            stale_dossiers = await self._repository.get_stale_draft_dossiers(
                cutoff_time=cutoff_time
            )

            if not stale_dossiers:
                return 0

            for dossier in stale_dossiers:
                expired_dossier = dossier.expire(now=execution_time)
                await self._repository.save(expired_dossier)

                event = DossierExpired(
                    dossier_id=expired_dossier.id,
                    vehicle_id=expired_dossier.vehicle_id,
                    expired_at=execution_time,
                )
                await self._event_bus.publish(event)

            await self._uow.commit()

        return len(stale_dossiers)
