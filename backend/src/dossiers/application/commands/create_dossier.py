"""Commande applicative de création d'un dossier brouillon."""

from dataclasses import dataclass
from uuid import UUID

from src.dossiers.domain.entities.dossier import Dossier
from src.dossiers.domain.ports.dossier_repository import DossierRepository
from src.dossiers.domain.value_objects.financing_plan import FinancingPlan
from src.dossiers.domain.value_objects.trade_in import TradeIn
from src.shared.domain.ports.unit_of_work import AbstractUnitOfWork


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
        uow: AbstractUnitOfWork,
    ) -> None:
        self._dossier_repository = dossier_repository
        self._uow = uow

    async def handle(self, command: CreateDossierCommand) -> Dossier:
        """Crée un dossier DRAFT et valide sa persistance."""
        dossier = Dossier.create(
            user_id=command.user_id,
            vehicle_id=command.vehicle_id,
            trade_in=command.trade_in,
            financing_plan=command.financing_plan,
        )

        async with self._uow:
            await self._dossier_repository.save(dossier)
            await self._uow.commit()

        return dossier
