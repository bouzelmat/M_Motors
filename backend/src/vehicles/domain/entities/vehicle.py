"""Entité métier représentant un véhicule du catalogue."""

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.shared.domain.entity import Entity
from src.shared.domain.exceptions import DomainError
from src.vehicles.domain.value_objects.catalog_type import CatalogType
from src.vehicles.domain.value_objects.energy_type import EnergyType
from src.vehicles.domain.value_objects.mileage import Mileage
from src.vehicles.domain.value_objects.price import Price
from src.vehicles.domain.value_objects.service_inclusion import ServiceInclusion
from src.vehicles.domain.value_objects.vehicle_status import VehicleStatus


@dataclass(frozen=True)
class Vehicle(Entity):
    id: UUID
    brand: str
    model: str
    year: int
    price: Price | None
    mileage: Mileage
    energy_type: EnergyType
    status: VehicleStatus
    catalog_type: CatalogType
    monthly_rent: Price | None = None
    description: str | None = None
    created_at: datetime = None
    updated_at: datetime = None
    services: list[ServiceInclusion] = field(default_factory=list)
    photo_url: str | None = None
    photo_key: str | None = None

    def __post_init__(self) -> None:
        if not self.brand or not self.model:
            raise DomainError("La marque et le modèle sont obligatoires.")

        current_year = datetime.now(timezone.utc).year
        if self.year < 1886 or self.year > current_year + 1:
            raise DomainError(f"Année invalide : {self.year}.")

        if self.catalog_type == CatalogType.SALE and (
            self.price is None or self.price.value <= 0
        ):
            raise DomainError(
                "Un véhicule en vente doit avoir un prix de vente valide."
            )

        if self.catalog_type == CatalogType.RENTAL and self.monthly_rent is None:
            raise DomainError("Un véhicule en location doit avoir un loyer mensuel.")

        if self.monthly_rent is not None and self.monthly_rent.value <= 0:
            raise DomainError("Le loyer mensuel doit être positif.")

        if isinstance(self.id, str):
            object.__setattr__(self, "id", UUID(self.id))
        if self.created_at is None:
            object.__setattr__(self, "created_at", datetime.now(timezone.utc))
        if self.updated_at is None:
            object.__setattr__(self, "updated_at", self.created_at)

    @classmethod
    def create(
        cls,
        brand: str,
        model: str,
        year: int,
        price: Price | None,
        mileage: Mileage,
        energy_type: EnergyType,
        catalog_type: CatalogType,
        monthly_rent: Price | None = None,
        description: str | None = None,
        services: list[ServiceInclusion] | None = None,
        photo_url: str | None = None,
        photo_key: str | None = None,
    ) -> "Vehicle":
        """Fabrique permettant de créer un nouveau véhicule avec validation des invariants métier."""
        if mileage.value < 0:
            raise DomainError("Le kilométrage ne peut pas être négatif.")

        now = datetime.now(timezone.utc)
        return cls(
            id=uuid4(),
            brand=brand,
            model=model,
            year=year,
            price=price,
            mileage=mileage,
            energy_type=energy_type,
            status=VehicleStatus.AVAILABLE,
            catalog_type=catalog_type,
            monthly_rent=monthly_rent,
            description=description,
            created_at=now,
            updated_at=now,
            services=services or [],
            photo_url=photo_url,
            photo_key=photo_key,
        )

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

    def get_services_with_inclusion(self) -> list[ServiceInclusion]:
        return list(self.services)

    def switch_to_rental(self, monthly_rent: Price) -> "Vehicle":
        """Basculer le véhicule en mode location (RENTAL). Efface le prix d'achat."""
        if self.catalog_type == CatalogType.RENTAL:
            raise DomainError("Le véhicule est déjà en mode location.")

        if monthly_rent is None or monthly_rent.value <= 0:
            raise DomainError("Le loyer mensuel doit être supérieur à zéro.")

        return replace(
            self,
            catalog_type=CatalogType.RENTAL,
            monthly_rent=monthly_rent,
            price=None,
            updated_at=datetime.now(timezone.utc),
        )

    def switch_to_sale(self, price: Price) -> "Vehicle":
        """Basculer le véhicule en mode vente (SALE). Efface le loyer mensuel."""
        if self.catalog_type == CatalogType.SALE:
            raise DomainError("Le véhicule est déjà en mode vente.")

        if price is None or price.value <= 0:
            raise DomainError("Le prix de vente doit être supérieur à zéro.")

        return replace(
            self,
            catalog_type=CatalogType.SALE,
            price=price,
            monthly_rent=None,
            updated_at=datetime.now(timezone.utc),
        )

    def toggle_catalog_type(self, new_price: Price) -> "Vehicle":
        """Bascule automatiquement le type de catalogue vers le mode opposé avec la nouvelle valeur tarifaire."""
        if self.catalog_type == CatalogType.SALE:
            return self.switch_to_rental(monthly_rent=new_price)
        return self.switch_to_sale(price=new_price)
