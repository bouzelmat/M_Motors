"""Schémas Pydantic pour les endpoints du contexte Véhicules."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_serializer  # <-- AJOUT


class ServiceDTO(BaseModel):
    """Représentation d'un service optionnel."""

    id: UUID
    name: str
    monthly_cost: Decimal
    category: str  # INSURANCE, ASSISTANCE, MAINTENANCE, INSPECTION

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

    @field_serializer('monthly_rent')
    def serialize_monthly_rent(self, value: Decimal | None) -> str | None:
        if value is None:
            return None
        return f"{value:.2f}"

    model_config = ConfigDict(from_attributes=True)


class VehicleDetailDTO(VehicleListItemDTO):
    """DTO pour les détails complets d'un véhicule."""

    price: Decimal  # Prix d'achat (utile pour comparaison)
    mileage: int
    energy_type: str
    description: str | None = None
    services: list[ServiceDTO] = Field(
        default_factory=list,
        description="Services disponibles avec coût et catégorie",
    )

    @field_serializer('price')
    def serialize_price(self, value: Decimal | None) -> str | None:
        if value is None:
            return None
        return f"{value:.2f}"

    model_config = ConfigDict(from_attributes=True)