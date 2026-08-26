"""Entité métier représentant un véhicule du catalogue."""

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from uuid import UUID

from src.shared.domain.entity import Entity
from src.shared.domain.exceptions import DomainError
from src.vehicles.domain.value_objects.catalog_type import CatalogType
from src.vehicles.domain.value_objects.energy_type import EnergyType
from src.vehicles.domain.value_objects.mileage import Mileage
from src.vehicles.domain.value_objects.price import Price
from src.vehicles.domain.value_objects.vehicle_status import VehicleStatus


@dataclass(frozen=True)
class Vehicle(Entity):
    id: UUID
    brand: str
    model: str
    year: int
    price: Price
    mileage: Mileage
    energy_type: EnergyType
    status: VehicleStatus
    catalog_type: CatalogType
    monthly_rent: Price | None = None
    description: str | None = None
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self) -> None:
        if not self.brand or not self.model:
            raise ValueError("La marque et le modèle sont obligatoires.")
        if self.year < 1886 or self.year > datetime.now(timezone.utc).year + 1:
            raise ValueError(f"Année invalide : {self.year}.")
        if self.catalog_type == CatalogType.RENTAL and self.monthly_rent is None:
            raise ValueError("Un véhicule en location doit avoir un loyer mensuel.")
        if self.monthly_rent is not None and self.monthly_rent.value <= 0:
            raise DomainError("Le loyer mensuel doit être positif.")
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
        return (
            self.status == VehicleStatus.AVAILABLE
            and self.catalog_type == CatalogType.RENTAL
        )

    def is_available_for_sale(self) -> bool:
        return (
            self.status == VehicleStatus.AVAILABLE
            and self.catalog_type == CatalogType.SALE
        )

    # Les méthodes de transition restent inchangées (rent, sell, mark_maintenance, make_available)
    # mais doivent conserver le catalog_type.
    def rent(self) -> "Vehicle":
        if not self.is_available_for_rental():
            raise DomainError(f"Véhicule {self.id} non disponible à la location.")
        return replace(
            self, status=VehicleStatus.RENTED, updated_at=datetime.now(timezone.utc)
        )

    def sell(self) -> "Vehicle":
        if not self.is_available_for_sale():
            raise DomainError(f"Véhicule {self.id} non disponible à la vente.")
        return replace(
            self, status=VehicleStatus.SOLD, updated_at=datetime.now(timezone.utc)
        )

    def mark_maintenance(self) -> "Vehicle":
        return replace(
            self,
            status=VehicleStatus.MAINTENANCE,
            updated_at=datetime.now(timezone.utc),
        )

    def make_available(self) -> "Vehicle":
        return replace(
            self, status=VehicleStatus.AVAILABLE, updated_at=datetime.now(timezone.utc)
        )
