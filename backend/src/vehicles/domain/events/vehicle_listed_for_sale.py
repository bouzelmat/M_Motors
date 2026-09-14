"""Événement publié après la bascule réussie d'un véhicule vers le catalogue vente."""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from src.shared.domain.events.domain_event import DomainEvent


@dataclass(frozen=True)
class VehicleListedForSale(DomainEvent):
    """Événement signifiant la mise en visibilité vente d'un véhicule."""

    vehicle_id: UUID
    previous_catalog_type: str
    new_catalog_type: str  # SALE
    new_price: Decimal
