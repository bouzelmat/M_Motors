"""Port définissant le contrat de persistance pour les véhicules."""

from typing import List, Optional, Protocol
from uuid import UUID

from vehicles.domain.entities.Vehicle import Vehicle


class VehicleRepository(Protocol):
    """Interface (port) que doit implémenter l'adaptateur d'infrastructure."""

    async def find_by_id(self, vehicle_id: UUID) -> Optional[Vehicle]:
        """Récupère un véhicule par son identifiant."""
        ...

    async def list_available_for_rental(
        self, skip: int = 0, limit: int = 100
    ) -> List[Vehicle]:
        """
        Récupère la liste des véhicules disponibles pour la location.
        - `skip` : nombre de véhicules à sauter (pagination)
        - `limit` : nombre maximal de véhicules à retourner
        """
        ...

    async def save(self, vehicle: Vehicle) -> None:
        """Persiste un véhicule (insert ou update)."""
        ...