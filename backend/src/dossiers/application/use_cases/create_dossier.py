"""Cas d'utilisation et commande applicative de création d'un dossier."""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from src.dossiers.domain.ports.vehicle_availability_port import VehicleAvailabilityPort
from src.dossiers.domain.entities.dossier import Dossier
from src.dossiers.domain.events.dossier_initialized import DossierInitialized
from src.dossiers.domain.exceptions import (
    VehicleNotAvailableException,
    VehicleNotFoundException,
)
from src.dossiers.domain.value_objects.financing_plan import FinancingPlan
from src.dossiers.domain.value_objects.trade_in import TradeIn
from src.shared.domain.ports.unit_of_work import AbstractUnitOfWork
from src.shared.infrastructure.event_bus import EventBus


@dataclass(frozen=True)
class TradeInDTO:
    registration: str
    mileage: int
    brand: str | None = None
    model: str | None = None


@dataclass(frozen=True)
class FinancingPlanDTO:
    down_payment: Decimal
    duration_months: int
    monthly_payment: Decimal


@dataclass(frozen=True)
class CreateDossierCommand:
    user_id: UUID
    vehicle_id: UUID
    trade_in: TradeInDTO | None = None
    financing_plan: FinancingPlanDTO | None = None


class CreateDossierCommandHandler:
    """Gestionnaire de commande créant un dossier et orchestrant sa persistance."""

    def __init__(
        self,
        uow: AbstractUnitOfWork,
        vehicle_availability_port: VehicleAvailabilityPort,
        event_bus: EventBus,
    ) -> None:
        self._uow = uow
        self._vehicle_port = vehicle_availability_port
        self._event_bus = event_bus

    async def __call__(self, command: CreateDossierCommand) -> Dossier:
        # 1. Vérifications véhicule
        if not await self._vehicle_port.exists(command.vehicle_id):
            raise VehicleNotFoundException(command.vehicle_id)

        if not await self._vehicle_port.is_available(command.vehicle_id):
            raise VehicleNotAvailableException(command.vehicle_id)

        # 2. Construction des Value Objects
        trade_in = None
        if command.trade_in is not None:
            trade_in = TradeIn(
                registration=command.trade_in.registration,
                mileage=command.trade_in.mileage,
                brand=command.trade_in.brand,
                model=command.trade_in.model,
            )

        financing_plan = None
        if command.financing_plan is not None:
            financing_plan = FinancingPlan(
                down_payment=command.financing_plan.down_payment,
                duration_months=command.financing_plan.duration_months,
                monthly_payment=command.financing_plan.monthly_payment,
            )

        # 3. Création de l'entité domaine (Statut DRAFT)
        dossier = Dossier.create(
            user_id=command.user_id,
            vehicle_id=command.vehicle_id,
            trade_in=trade_in,
            financing_plan=financing_plan,
        )

        # 4. Exécution dans l'Unité de Travail
        async with self._uow:
            await self._uow.dossiers.save(dossier)

            # 5. Publication de l'événement de domaine
            event = DossierInitialized(
                dossier_id=dossier.id,
                user_id=dossier.user_id,
                vehicle_id=dossier.vehicle_id,
            )
            await self._event_bus.publish(event)

            # 6. Validation définitive de la transaction
            await self._uow.commit()

        return dossier
