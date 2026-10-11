"""Commandes d'administration pour modifier et supprimer un véhicule."""

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from src.shared.domain.exceptions import DomainError
from src.shared.domain.ports.unit_of_work import AbstractUnitOfWork
from src.vehicles.application.commands.add_vehicle import VehicleServiceSelection
from src.vehicles.domain.entities.vehicle import Vehicle
from src.vehicles.domain.ports.vehicle_repository import VehicleRepository
from src.vehicles.domain.value_objects.catalog_type import CatalogType
from src.vehicles.domain.value_objects.energy_type import EnergyType
from src.vehicles.domain.value_objects.mileage import Mileage
from src.vehicles.domain.value_objects.price import Price


@dataclass(frozen=True)
class UpdateVehicleCommand:
    """Données complètes d'une modification de véhicule."""

    vehicle_id: UUID
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


class UpdateVehicleCommandHandler:
    """Valide et persiste les changements d'un véhicule existant."""

    def __init__(self, repository: VehicleRepository, uow: AbstractUnitOfWork) -> None:
        self._repository = repository
        self._uow = uow

    async def handle(self, command: UpdateVehicleCommand) -> Vehicle:
        async with self._uow:
            vehicle = await self._repository.find_by_id_for_update(command.vehicle_id)
            if vehicle is None:
                raise DomainError(f"Véhicule {command.vehicle_id} introuvable.")

            service_catalog = {
                service.service_id: service
                for service in await self._repository.list_service_catalog()
            }
            if len({service.service_id for service in command.services}) != len(
                command.services
            ):
                raise DomainError(
                    "Un service ne peut être sélectionné qu'une seule fois."
                )

            services = []
            for selection in command.services:
                service = service_catalog.get(selection.service_id)
                if service is None:
                    raise DomainError("Un des services sélectionnés est indisponible.")
                services.append(replace(service, included=selection.included))

            updated_vehicle = replace(
                vehicle,
                brand=command.brand,
                model=command.model,
                year=command.year,
                mileage=Mileage(command.mileage),
                energy_type=command.energy_type,
                catalog_type=command.catalog_type,
                price=(
                    Price(float(command.price)) if command.price is not None else None
                ),
                monthly_rent=(
                    Price(float(command.monthly_rent))
                    if command.monthly_rent is not None
                    else None
                ),
                description=command.description,
                services=services,
                updated_at=datetime.now(timezone.utc),
            )

            await self._repository.save(updated_vehicle)
            await self._uow.commit()
        return updated_vehicle


@dataclass(frozen=True)
class DeleteVehicleCommand:
    """Identifiant du véhicule à supprimer."""

    vehicle_id: UUID


class DeleteVehicleCommandHandler:
    """Supprime un véhicule existant dans une transaction."""

    def __init__(self, repository: VehicleRepository, uow: AbstractUnitOfWork) -> None:
        self._repository = repository
        self._uow = uow

    async def handle(self, command: DeleteVehicleCommand) -> None:
        async with self._uow:
            deleted = await self._repository.delete_by_id(command.vehicle_id)
            if not deleted:
                raise DomainError(f"Véhicule {command.vehicle_id} introuvable.")
            await self._uow.commit()
