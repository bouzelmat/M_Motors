"""Command et Command Handler pour l'ajout d'un véhicule."""

from dataclasses import dataclass, replace
from decimal import Decimal
from uuid import UUID

from src.shared.domain.ports.event_bus import AbstractEventBus
from src.shared.domain.ports.unit_of_work import AbstractUnitOfWork
from src.shared.domain.exceptions import DomainError
from src.vehicles.domain.entities.vehicle import Vehicle
from src.vehicles.domain.events.vehicle_added import VehicleAdded
from src.vehicles.domain.ports.vehicle_repository import VehicleRepository
from src.vehicles.domain.value_objects.catalog_type import CatalogType
from src.vehicles.domain.value_objects.energy_type import EnergyType
from src.vehicles.domain.value_objects.mileage import Mileage
from src.vehicles.domain.value_objects.price import Price
from src.vehicles.domain.value_objects.service_inclusion import ServiceInclusion


@dataclass(frozen=True)
class VehicleServiceSelection:
    """Identifie un service du catalogue et son inclusion dans l'offre."""

    service_id: UUID
    included: bool


@dataclass(frozen=True)
class AddVehicleCommand:
    """Commande transportant les données nécessaires à la création d'un véhicule."""

    brand: str
    model: str
    year: int
    mileage: int
    energy_type: EnergyType
    catalog_type: CatalogType
    price: Decimal | None = None
    monthly_rent: Decimal | None = None
    description: str | None = None
    services: tuple[VehicleServiceSelection, ...] = ()


class AddVehicleCommandHandler:
    """Orchestrateur du cas d'usage de création d'un véhicule."""

    def __init__(
        self,
        repository: VehicleRepository,
        uow: AbstractUnitOfWork,
        event_bus: AbstractEventBus,
    ) -> None:
        self._repository = repository
        self._uow = uow
        self._event_bus = event_bus

    async def handle(self, command: AddVehicleCommand) -> Vehicle:
        """Exécute la commande de création d'un véhicule.

        Raises:
            DomainError: Si les invariants du domaine ne sont pas respectés.
        """
        price_vo = Price(command.price) if command.price is not None else None
        rent_vo = (
            Price(command.monthly_rent) if command.monthly_rent is not None else None
        )
        mileage_vo = Mileage(command.mileage)

        services = await self._resolve_services(command.services)

        # Instanciation et validation des invariants via la fabrique du domaine
        vehicle = Vehicle.create(
            brand=command.brand,
            model=command.model,
            year=command.year,
            price=price_vo,
            mileage=mileage_vo,
            energy_type=command.energy_type,
            catalog_type=command.catalog_type,
            monthly_rent=rent_vo,
            description=command.description,
            services=services,
        )

        async with self._uow:
            # 1. Sauvegarde en base via le repository
            await self._repository.save(vehicle)

            # 2. Publication de l'événement de domaine
            event = VehicleAdded(
                vehicle_id=vehicle.id,
                brand=vehicle.brand,
                model=vehicle.model,
                catalog_type=vehicle.catalog_type.value,
            )
            await self._event_bus.publish(event)

            # 3. Validation de la transaction
            await self._uow.commit()

        return vehicle

    async def _resolve_services(
        self,
        selections: tuple[VehicleServiceSelection, ...],
    ) -> list[ServiceInclusion]:
        if not selections:
            return []

        if len({selection.service_id for selection in selections}) != len(selections):
            raise DomainError("Un service ne peut être sélectionné qu'une seule fois.")

        service_catalog = {
            service.service_id: service
            for service in await self._repository.list_service_catalog()
        }
        resolved_services = []
        for selection in selections:
            service = service_catalog.get(selection.service_id)
            if service is None:
                raise DomainError("Un des services sélectionnés est indisponible.")
            resolved_services.append(replace(service, included=selection.included))
        return resolved_services
