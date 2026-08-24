from typing import Protocol
from uuid import UUID

from src.vehicles.domain.entities.Vehicle import Vehicle
from src.vehicles.domain.value_objects.VehicleSearchCriteria import (
    VehicleSearchCriteria,
)


class VehicleRepository(Protocol):
    """Port pour la persistance des véhicules."""

    async def save(self, vehicle: Vehicle) -> None:
        """Sauvegarde un véhicule (insertion ou mise à jour)."""
        ...

    async def find_by_id(self, vehicle_id: UUID) -> Vehicle | None:
        """Récupère un véhicule par son identifiant."""
        ...

    async def find_by_criteria(self, criteria: VehicleSearchCriteria) -> list[Vehicle]:
        """Recherche des véhicules selon les critères donnés."""
        ...
