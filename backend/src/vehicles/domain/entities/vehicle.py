"""Entité métier représentant un véhicule du catalogue."""

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from shared.domain.entity import Entity
from shared.domain.exceptions import DomainError
from vehicles.domain.value_objects.CatalogType import CatalogType
from vehicles.domain.value_objects.EnergyType import EnergyType
from vehicles.domain.value_objects.Mileage import Mileage
from vehicles.domain.value_objects.Price import Price
from vehicles.domain.value_objects.VehicleStatus import VehicleStatus


@dataclass(frozen=True)
class Vehicle(Entity[UUID]):
    id: UUID
    brand: str
    model: str
    year: int
    price: Price
    mileage: Mileage
    energy_type: EnergyType
    status: VehicleStatus
    catalog_type: CatalogType 
    description: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self) -> None:
        if not self.brand or not self.model:
            raise ValueError("La marque et le modèle sont obligatoires.")
        if self.year < 1886 or self.year > datetime.now().year + 1:
            raise ValueError(f"Année invalide : {self.year}.")
        if isinstance(self.id, str):
            object.__setattr__(self, "id", UUID(self.id))
        if self.created_at is None:
            object.__setattr__(self, "created_at", datetime.now(timezone.utc))
        if self.updated_at is None:
            object.__setattr__(self, "updated_at", self.created_at)

    @property
    def full_name(self) -> str:
        return f"{self.brand} {self.model} ({self.year})"

    def is_available_for_rental(self) -> bool:
        return self.status == VehicleStatus.AVAILABLE and self.catalog_type == CatalogType.RENTAL

    def is_available_for_sale(self) -> bool:
        return self.status == VehicleStatus.AVAILABLE and self.catalog_type == CatalogType.SALE

    # Les méthodes de transition restent inchangées (rent, sell, mark_maintenance, make_available)
    # mais doivent conserver le catalog_type.
    def rent(self) -> "Vehicle":
        if not self.is_available_for_rental():
            raise DomainError(f"Véhicule {self.id} non disponible à la location.")
        return replace(self, status=VehicleStatus.RENTED, updated_at=datetime.now(timezone.utc))

    def sell(self) -> "Vehicle":
        if not self.is_available_for_sale():
            raise DomainError(f"Véhicule {self.id} non disponible à la vente.")
        return replace(self, status=VehicleStatus.SOLD, updated_at=datetime.now(timezone.utc))

    def mark_maintenance(self) -> "Vehicle":
        return replace(self, status=VehicleStatus.MAINTENANCE, updated_at=datetime.now(timezone.utc))

    def make_available(self) -> "Vehicle":
        return replace(self, status=VehicleStatus.AVAILABLE, updated_at=datetime.now(timezone.utc))