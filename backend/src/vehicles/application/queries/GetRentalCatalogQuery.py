from dataclasses import dataclass
from decimal import Decimal

from src.vehicles.domain.entities.Vehicle import Vehicle
from src.vehicles.domain.ports.VehicleRepository import VehicleRepository
from src.vehicles.domain.value_objects.VehicleSearchCriteria import (
    VehicleSearchCriteria,
)


@dataclass(frozen=True)
class GetRentalCatalogQuery:
    """Requête pour obtenir le catalogue des véhicules disponibles en location (LLD)."""

    max_monthly_rent: Decimal | None = (
        None  # D'autres filtres (marque, carburant, kilométrage) seront ajoutés ultérieurement
    )


class GetRentalCatalogQueryHandler:
    """Handler pour la requête GetRentalCatalogQuery."""

    def __init__(self, repository: VehicleRepository) -> None:
        self._repository = repository

    async def handle(self, query: GetRentalCatalogQuery) -> list[Vehicle]:
        """
        Exécute la requête et retourne la liste des véhicules disponibles en location.
        """
        criteria = VehicleSearchCriteria(
            mode="rental",
            max_monthly_rent=query.max_monthly_rent,
        )
        return await self._repository.find_by_criteria(criteria)
