from dataclasses import dataclass
from uuid import UUID

from src.vehicles.domain.entities.service import Service
from src.vehicles.domain.entities.vehicle import Vehicle
from src.vehicles.domain.ports.vehicle_repository import VehicleRepository


@dataclass(frozen=True, slots=True)
class GetVehicleDetailQuery:
    """Requête permettant de récupérer le détail d'un véhicule."""

    vehicle_id: UUID


class GetVehicleDetailQueryHandler:
    """Traite la récupération du détail d'un véhicule."""

    def __init__(
        self,
        repository: VehicleRepository,
    ) -> None:
        self._repository = repository

    async def handle(
        self,
        query: GetVehicleDetailQuery,
    ) -> tuple[Vehicle, list[Service]] | None:
        """Retourne le véhicule demandé avec ses services."""

        return await self._repository.find_by_id_with_services(
            query.vehicle_id,
        )
