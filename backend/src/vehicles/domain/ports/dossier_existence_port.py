"""Port secondaire définissant le contrat de vérification des dossiers actifs pour un véhicule."""

from typing import Protocol
from uuid import UUID


class DossierExistencePort(Protocol):
    """Contrat d'infrastructure permettant au domaine vehicles de vérifier la présence d'un dossier actif."""

    async def has_active_dossier_for_vehicle(
        self,
        vehicle_id: UUID,
    ) -> bool:
        """Détermine si un dossier actif (DRAFT non expiré ou SUBMITTED) est rattaché au véhicule."""
        ...
