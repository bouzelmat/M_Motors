"""Port de consultation de l'existence de dossiers actifs pour un véhicule."""

from typing import Protocol
from uuid import UUID


class DossierExistencePort(Protocol):
    """Contrat d'intégration exposant la vérification de présence de dossiers actifs."""

    async def has_active_dossier_for_vehicle(
        self,
        vehicle_id: UUID,
    ) -> bool:
        """Vérifie si un dossier actif (SUBMITTED ou DRAFT non expiré) est lié au véhicule."""
        ...
