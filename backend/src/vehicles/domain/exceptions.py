"""Exceptions spécifiques au contexte Véhicules."""

from shared.domain.exceptions import DomainError, NotFoundError


class VehicleNotFoundError(NotFoundError):
    """Levée lorsqu'un véhicule demandé n'existe pas en base."""

    def __init__(self, vehicle_id: str) -> None:
        super().__init__(f"Véhicule avec l'identifiant {vehicle_id} introuvable.")
        self.vehicle_id = vehicle_id


class VehicleNotAvailableError(DomainError):
    """Levée lorsqu'on tente de louer/acheter un véhicule indisponible."""

    def __init__(self, vehicle_id: str) -> None:
        super().__init__(f"Le véhicule {vehicle_id} n'est pas disponible pour la location.")
        self.vehicle_id = vehicle_id
