"""Command et Command Handler pour la bascule du mode commercial d'un véhicule (US-402)."""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from src.shared.domain.exceptions import DomainError
from src.shared.domain.ports.event_bus import AbstractEventBus
from src.shared.domain.ports.unit_of_work import AbstractUnitOfWork
from src.vehicles.application.exceptions import ActiveDossierWarningException
from src.vehicles.domain.entities.vehicle import Vehicle
from src.vehicles.domain.events.vehicle_listed_for_rental import VehicleListedForRental
from src.vehicles.domain.events.vehicle_listed_for_sale import VehicleListedForSale
from src.vehicles.domain.ports.dossier_existence_port import DossierExistencePort
from src.vehicles.domain.ports.vehicle_repository import VehicleRepository
from src.vehicles.domain.value_objects.catalog_type import CatalogType
from src.vehicles.domain.value_objects.price import Price


@dataclass(frozen=True)
class ToggleVehicleTypeCommand:
    """Commande de bascule du mode commercial (vente <-> location) d'un véhicule."""

    vehicle_id: UUID
    new_price: Decimal
    bypass_warning: bool = False


class ToggleVehicleTypeCommandHandler:
    """Orchestrateur du cas d'usage de bascule vente/location (US-402)."""

    def __init__(
        self,
        repository: VehicleRepository,
        uow: AbstractUnitOfWork,
        event_bus: AbstractEventBus,
        dossier_existence_port: DossierExistencePort,
    ) -> None:
        self._repository = repository
        self._uow = uow
        self._event_bus = event_bus
        self._dossier_existence_port = dossier_existence_port

    async def handle(self, command: ToggleVehicleTypeCommand) -> Vehicle:
        """Exécute la commande de bascule de mode commercial.

        Raises:
            DomainError: Si le véhicule est introuvable ou si les invariants de domaine
                sont violés (ex. tarif <= 0).
            ActiveDossierWarningException: Si un dossier actif existe et que
                bypass_warning est False.
        """
        vehicle = await self._repository.get_by_id(command.vehicle_id)
        if vehicle is None:
            raise DomainError(f"Véhicule introuvable : {command.vehicle_id}")

        has_active_dossier = (
            await self._dossier_existence_port.has_active_dossier_for_vehicle(
                vehicle_id=command.vehicle_id
            )
        )

        if has_active_dossier and not command.bypass_warning:
            raise ActiveDossierWarningException(vehicle_id=command.vehicle_id)

        previous_catalog_type = vehicle.catalog_type
        new_price_vo = Price(command.new_price)

        # Délégation explicite à l'entité métier
        updated_vehicle = vehicle.toggle_catalog_type(new_price=new_price_vo)
        new_catalog_type = updated_vehicle.catalog_type

        async with self._uow:
            await self._repository.save(updated_vehicle)

            if new_catalog_type == CatalogType.RENTAL:
                event = VehicleListedForRental(
                    vehicle_id=updated_vehicle.id,
                    previous_catalog_type=previous_catalog_type.value,
                    new_catalog_type=new_catalog_type.value,
                    new_monthly_rent=command.new_price,
                )
            else:
                event = VehicleListedForSale(
                    vehicle_id=updated_vehicle.id,
                    previous_catalog_type=previous_catalog_type.value,
                    new_catalog_type=new_catalog_type.value,
                    new_price=command.new_price,
                )

            await self._event_bus.publish(event)
            await self._uow.commit()

        return updated_vehicle
