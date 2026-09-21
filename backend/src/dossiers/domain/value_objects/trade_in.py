"""Objet de valeur représentant le véhicule de reprise."""

from dataclasses import dataclass
from decimal import Decimal

from src.shared.domain.exceptions import DomainError


@dataclass(frozen=True)
class TradeIn:
    """Informations sur l'ancien véhicule à reprendre."""

    registration: str
    mileage: int
    brand: str | None = None
    model: str | None = None
    estimated_value: Decimal | None = None

    def __post_init__(self) -> None:
        """Valide les contraintes de l'offre de reprise."""
        if not self.registration or not self.registration.strip():
            raise DomainError(
                "L'immatriculation du véhicule de reprise ne peut pas être vide."
            )

        if self.mileage < 0:
            raise DomainError(
                "Le kilométrage du véhicule de reprise ne peut pas être négatif."
            )
