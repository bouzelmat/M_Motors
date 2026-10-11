from typing import Protocol
from uuid import UUID

from src.vehicles.domain.entities.vehicle import Vehicle
from src.vehicles.domain.entities.vehicle_photo import VehiclePhoto
from src.vehicles.domain.value_objects.service_inclusion import ServiceInclusion
from src.vehicles.domain.value_objects.vehicle_search_criteria import (
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

    async def list_all(self) -> list[Vehicle]:
        """Retourne tous les véhicules, quel que soit leur statut."""
        ...

    async def delete_by_id(self, vehicle_id: UUID) -> bool:
        """Supprime un véhicule et ses ressources dépendantes."""
        ...

    async def find_by_id_for_update(self, vehicle_id: UUID) -> Vehicle | None:
        """Récupère un véhicule en verrouillant sa ligne jusqu'à la fin de la transaction."""
        ...

    async def find_by_criteria(self, criteria: VehicleSearchCriteria) -> list[Vehicle]:
        """Recherche des véhicules selon les critères donnés."""
        ...

    async def list_service_catalog(self) -> list[ServiceInclusion]:
        """Retourne les services disponibles dans le catalogue commun."""
        ...

    async def list_uploaded_photos(self, vehicle_id: UUID) -> list[VehiclePhoto]:
        """Retourne les photos confirmées d'un véhicule."""
        ...

    async def set_primary_photo(self, vehicle_id: UUID, photo_id: UUID) -> bool:
        """Définit une photo confirmée comme photo principale."""
        ...

    async def delete_photo(self, vehicle_id: UUID, photo_id: UUID) -> str | None:
        """Supprime une photo et retourne sa clé de stockage, si elle existe."""
        ...
