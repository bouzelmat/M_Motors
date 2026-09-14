"""Exceptions spécifiques au contexte Véhicules."""

from src.shared.domain.exceptions import DomainError, NotFoundError


class VehicleNotFoundError(NotFoundError):
    """Levée lorsqu'un véhicule demandé n'existe pas en base."""

    def __init__(self, vehicle_id: str) -> None:
        super().__init__(f"Véhicule avec l'identifiant {vehicle_id} introuvable.")
        self.vehicle_id = vehicle_id


class VehicleNotAvailableError(DomainError):
    """Levée lorsqu'on tente de louer/acheter un véhicule indisponible."""

    def __init__(self, vehicle_id: str) -> None:
        super().__init__(
            f"Le véhicule {vehicle_id} n'est pas disponible pour la location."
        )
        self.vehicle_id = vehicle_id


class InvalidImageFormatError(DomainError):
    """Levée lorsque le type MIME du fichier n'est pas une image autorisée."""

    def __init__(self, content_type: str) -> None:
        super().__init__(
            f"Format de fichier non autorisé : '{content_type}'. Formats acceptés : JPEG, PNG, WEBP."
        )


class FileSizeExceededError(DomainError):
    """Levée lorsque la taille déclarée dépasse 10 Mo."""

    def __init__(self, size: int, max_size: int = 10 * 1024 * 1024) -> None:
        super().__init__(
            f"Taille de fichier ({size} octets) supérieure à la limite ({max_size} octets)."
        )
