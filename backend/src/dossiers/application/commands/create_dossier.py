"""Commande applicative de création d'un dossier brouillon."""

from dataclasses import dataclass
from uuid import UUID

from src.dossiers.domain.entities.dossier import Dossier
from src.dossiers.domain.events.dossier_initialized import DossierInitialized
from src.dossiers.domain.exceptions import (
    VehicleNotAvailableException,
    VehicleNotFoundException,
)
from src.dossiers.domain.ports.dossier_repository import DossierRepository
from src.dossiers.domain.value_objects.financing_plan import FinancingPlan
from src.dossiers.domain.value_objects.trade_in import TradeIn
from src.shared.domain.ports.unit_of_work import AbstractUnitOfWork
from src.shared.domain.ports.event_bus import AbstractEventBus
from src.vehicles.domain.ports.vehicle_repository import VehicleRepository
from src.vehicles.domain.value_objects.vehicle_status import VehicleStatus


@dataclass(frozen=True)
class CreateDossierCommand:
    """Données nécessaires à la création d'un dossier."""

    user_id: UUID
    vehicle_id: UUID
    trade_in: TradeIn | None = None
    financing_plan: FinancingPlan | None = None


class CreateDossierCommandHandler:
    """Crée et persiste un dossier brouillon dans une transaction."""

    def __init__(
        self,
        dossier_repository: DossierRepository,
        vehicle_repository: VehicleRepository,
        uow: AbstractUnitOfWork,
        event_bus: AbstractEventBus,
    ) -> None:
        self._dossier_repository = dossier_repository
        self._vehicle_repository = vehicle_repository
        self._uow = uow
        self._event_bus = event_bus

    async def handle(self, command: CreateDossierCommand) -> Dossier:
        """Crée un dossier DRAFT et valide sa persistance."""
        async with self._uow:
            vehicle = await self._vehicle_repository.find_by_id_for_update(
                command.vehicle_id
            )
            if vehicle is None:
                raise VehicleNotFoundException(command.vehicle_id)
            if (
                vehicle.status != VehicleStatus.AVAILABLE
                or await self._dossier_repository.has_active_for_vehicle(
                    command.vehicle_id
                )
            ):
                raise VehicleNotAvailableException(command.vehicle_id)

            dossier = Dossier.create(
                user_id=command.user_id,
                vehicle_id=command.vehicle_id,
                trade_in=command.trade_in,
                financing_plan=command.financing_plan,
            )
            await self._dossier_repository.save(dossier)
            await self._event_bus.publish(
                DossierInitialized(
                    dossier_id=dossier.id,
                    user_id=dossier.user_id,
                    vehicle_id=dossier.vehicle_id,
                )
            )
            await self._uow.commit()

        return dossier
