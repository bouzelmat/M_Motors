"""Objet de valeur représentant le plan de financement d'un dossier."""

from dataclasses import dataclass
from decimal import Decimal

from src.shared.domain.exceptions import DomainError


@dataclass(frozen=True)
class FinancingPlan:
    """Plan de financement associé à une demande de dossier."""

    down_payment: Decimal
    duration_months: int
    monthly_payment: Decimal

    def __post_init__(self) -> None:
        """Valide l'intégrité du plan de financement."""
        if self.down_payment < Decimal("0"):
            raise DomainError("L'apport initial ne peut pas être négatif.")

        if self.duration_months <= 0:
            raise DomainError("La durée du financement doit être supérieure à 0 mois.")

        if self.monthly_payment < Decimal("0"):
            raise DomainError("La mensualité ne peut pas être négative.")
