"""Port applicatif pour vérifier la disponibilité d'un véhicule."""

from typing import Protocol
from uuid import UUID


class VehicleAvailabilityPort(Protocol):
    """Interface pour l'accès aux informations de disponibilité d'un véhicule."""

    async def is_available(self, vehicle_id: UUID) -> bool:
        """Indique si le véhicule existe et est disponible à la vente ou location."""
        ...

    async def exists(self, vehicle_id: UUID) -> bool:
        """Indique si le véhicule existe dans le catalogue."""
        ...