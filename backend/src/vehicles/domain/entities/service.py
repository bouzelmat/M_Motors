"""Entité domaine représentant un service optionnel."""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from src.shared.domain.entity import Entity
from src.vehicles.domain.value_objects.service_category import ServiceCategory


@dataclass(frozen=True)
class Service(Entity):
    """Représente un service optionnel disponible pour les véhicules."""

    id: UUID
    name: str
    monthly_cost: Decimal
    category: ServiceCategory

    def __post_init__(self) -> None:
        """Valide les données du service."""

        if not self.name:
            raise ValueError("Le nom du service est obligatoire.")

        if self.monthly_cost < 0:
            raise ValueError(
                "Le coût mensuel du service ne peut pas être négatif."
            )