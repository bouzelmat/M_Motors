"""Objet‑valeur représentant le kilométrage (en km)."""

from dataclasses import dataclass

from src.shared.domain.exceptions import DomainError


@dataclass(frozen=True)
class Mileage:
    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise DomainError("Le kilométrage ne peut pas être négatif.")
