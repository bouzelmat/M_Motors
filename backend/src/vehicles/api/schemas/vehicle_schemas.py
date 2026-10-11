"""Schémas Pydantic pour les endpoints du contexte Véhicules."""

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)

from src.vehicles.domain.value_objects.catalog_type import CatalogType
from src.vehicles.domain.value_objects.energy_type import EnergyType
from src.vehicles.domain.value_objects.mileage import Mileage
from src.vehicles.domain.value_objects.price import Price
from src.vehicles.domain.value_objects.vehicle_status import VehicleStatus


class ServiceDTO(BaseModel):
    """Représentation d'un service disponible."""

    id: UUID
    name: str
    monthly_cost: Decimal
    category: str  # INSURANCE, ASSISTANCE, MAINTENANCE, INSPECTION
    included: bool

    model_config = ConfigDict(from_attributes=True)


class VehicleListItemDTO(BaseModel):
    """DTO pour un véhicule dans la liste du catalogue (résumé)."""

    id: UUID
    brand: str
    model: str
    year: int
    monthly_rent: Decimal | None = None
    photo_url: str | None = Field(
        default=None,
        description="URL de la première photo (ou placeholder)",
    )
    included_services: list[str] = Field(
        default_factory=list,
        description="Noms des services inclus",
    )

    @field_validator("monthly_rent", mode="before")
    @classmethod
    def extract_monthly_rent(cls, v: Any) -> Decimal | None:
        if isinstance(v, Price):
            return v.value
        return v

    @field_serializer("monthly_rent")
    def serialize_monthly_rent(self, value: Decimal | None) -> str | None:
        if value is None:
            return None
        return f"{value:.2f}"

    model_config = ConfigDict(from_attributes=True)


class VehicleDetailDTO(VehicleListItemDTO):
    """DTO pour les détails complets d'un véhicule."""

    catalog_type: CatalogType
    price: Decimal | None = None
    mileage: int
    energy_type: str
    description: str | None = None
    services: list[ServiceDTO] = Field(
        default_factory=list,
        description="Services disponibles avec coût et catégorie",
    )

    @field_validator("price", mode="before")
    @classmethod
    def extract_price(cls, v: Any) -> Decimal | None:
        if isinstance(v, Price):
            return v.value
        return v

    @field_validator("mileage", mode="before")
    @classmethod
    def extract_mileage(cls, v: Any) -> int:
        if isinstance(v, Mileage):
            return v.value
        return v

    @field_serializer("price")
    def serialize_price(self, value: Decimal | None) -> str | None:
        if value is None:
            return None
        return f"{value:.2f}"

    model_config = ConfigDict(from_attributes=True)


class VehicleServiceSelectionRequest(BaseModel):
    """Service du catalogue à proposer sur le véhicule et son statut d'inclusion."""

    service_id: UUID
    included: bool = False


class CreateVehicleRequest(BaseModel):
    """DTO pour la création d'un véhicule via POST /vehicles."""

    brand: str = Field(..., min_length=1)
    model: str = Field(..., min_length=1)
    year: int = Field(..., ge=1886)
    mileage: int = Field(..., ge=0)
    energy_type: EnergyType
    catalog_type: CatalogType
    price: Decimal | None = Field(default=None, gt=0)
    monthly_rent: Decimal | None = Field(default=None, gt=0)
    description: str | None = None
    services: list[VehicleServiceSelectionRequest] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_catalog_type_requirements(self) -> "CreateVehicleRequest":
        if self.catalog_type == CatalogType.SALE and self.price is None:
            raise ValueError("Un véhicule en vente doit avoir un prix (price).")

        if self.catalog_type == CatalogType.RENTAL and self.monthly_rent is None:
            raise ValueError(
                "Un véhicule en location doit avoir un loyer mensuel (monthly_rent)."
            )

        if self.catalog_type == CatalogType.SALE and self.services:
            raise ValueError("Les services d'abonnement sont réservés à la location.")

        service_ids = [service.service_id for service in self.services]
        if len(service_ids) != len(set(service_ids)):
            raise ValueError("Un service ne peut être sélectionné qu'une seule fois.")

        return self


class ToggleCatalogTypeRequest(BaseModel):
    """DTO d'entrée pour PATCH /vehicles/{vehicle_id}/catalog-type.

    Le véhicule bascule automatiquement vers le mode opposé à son
    catalog_type courant (décision du domaine, cf. Vehicle.toggle_catalog_type).
    Cette requête ne précise pas de direction cible, seulement la nouvelle
    valeur tarifaire et la confirmation éventuelle.
    """

    new_price: Decimal = Field(
        ...,
        gt=0,
        description=(
            "Loyer mensuel ou prix de vente selon le mode résultant, "
            "déterminé côté serveur en fonction du catalog_type actuel."
        ),
    )
    confirm: bool = Field(
        default=False,
        description="Forcer la bascule même si un dossier actif existe (bypass_warning).",
    )


class VehicleResponse(BaseModel):
    """DTO de réponse après création ou consultation d'un véhicule."""

    id: UUID
    brand: str
    model: str
    year: int
    price: Decimal | None = None
    mileage: int
    energy_type: EnergyType
    status: VehicleStatus
    catalog_type: CatalogType
    monthly_rent: Decimal | None = None
    description: str | None = None
    created_at: datetime
    updated_at: datetime

    @field_validator("price", "monthly_rent", mode="before")
    @classmethod
    def extract_price_value(cls, v: Any) -> Decimal | None:
        if isinstance(v, Price):
            return v.value
        return v

    @field_validator("mileage", mode="before")
    @classmethod
    def extract_mileage_value(cls, v: Any) -> int:
        if isinstance(v, Mileage):
            return v.value
        return v

    model_config = ConfigDict(from_attributes=True)
