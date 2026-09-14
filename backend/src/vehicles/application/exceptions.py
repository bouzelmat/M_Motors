"""Exceptions spécifiques aux cas d'usage applicatifs du module vehicles."""

from uuid import UUID


class ActiveDossierWarningException(Exception):
    """Levée lorsqu'une bascule de catalogue est tentée sur un véhicule ayant un dossier actif sans confirmation."""

    def __init__(self, vehicle_id: UUID) -> None:
        self.vehicle_id = vehicle_id
        super().__init__(
            f"Le véhicule {vehicle_id} a un dossier actif. "
            "Confirmation requise pour poursuivre (bypass_warning=True)."
        )
