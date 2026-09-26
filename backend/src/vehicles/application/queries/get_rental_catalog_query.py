from dataclasses import dataclass
from decimal import Decimal

from src.vehicles.application.queries.search_vehicles_query import (
    SearchVehiclesQuery,
    SearchVehiclesQueryHandler,
)
from src.vehicles.domain.entities.vehicle import Vehicle
from src.vehicles.domain.ports.vehicle_repository import VehicleRepository
from src.vehicles.domain.value_objects.vehicle_search_criteria import (
    VehicleSearchCriteria,
)


@dataclass(frozen=True, slots=True)
class GetRentalCatalogQuery:
    """Requête pour obtenir le catalogue des véhicules disponibles en location."""

    max_monthly_rent: Decimal | None = None


class GetRentalCatalogQueryHandler:
    """Handler conservé pour la compatibilité avec le catalogue LLD."""

    def __init__(self, repository: VehicleRepository) -> None:
        self._search_handler = SearchVehiclesQueryHandler(repository)

    async def handle(self, query: GetRentalCatalogQuery) -> list[Vehicle]:
        """Exécute la recherche des véhicules en location."""

        criteria = VehicleSearchCriteria(
            mode="rental",
            max_monthly_rent=query.max_monthly_rent,
        )

        return await self._search_handler.handle(
            SearchVehiclesQuery(criteria=criteria),
        )
