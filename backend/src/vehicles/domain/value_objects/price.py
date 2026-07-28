"""Objet‑valeur représentant un prix (en euros)."""

from dataclasses import dataclass

from shared.domain.exceptions import DomainError


@dataclass(frozen=True)
class Price:
    value: float

    def __post_init__(self) -> None:
        if self.value < 0:
            raise DomainError("Le prix ne peut pas être négatif.")
        # Arrondi à 2 décimales pour la monnaie
        object.__setattr__(self, "value", round(self.value, 2))

    def __str__(self) -> str:
        return f"{self.value:.2f} €"