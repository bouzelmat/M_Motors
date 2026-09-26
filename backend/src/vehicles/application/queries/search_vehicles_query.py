from dataclasses import dataclass

from src.vehicles.domain.entities.vehicle import Vehicle
from src.vehicles.domain.ports.vehicle_repository import VehicleRepository
from src.vehicles.domain.value_objects.vehicle_search_criteria import (
    VehicleSearchCriteria,
)


@dataclass(frozen=True, slots=True)
class SearchVehiclesQuery:
    """Requête générique de recherche de véhicules."""

    criteria: VehicleSearchCriteria


class SearchVehiclesQueryHandler:
    """Handler générique pour rechercher des véhicules."""

    def __init__(self, repository: VehicleRepository) -> None:
        self._repository = repository

    async def handle(
        self,
        query: SearchVehiclesQuery,
    ) -> list[Vehicle]:
        """Retourne les véhicules correspondant aux critères."""

        return await self._repository.find_by_criteria(
            query.criteria,
        )
