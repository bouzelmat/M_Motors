"""Événement émis lors du changement de mode commercial d'un véhicule."""

from dataclasses import dataclass
from uuid import UUID

from src.shared.domain.events.domain_event import DomainEvent


@dataclass(frozen=True)
class VehicleCatalogTypeChanged(DomainEvent):
    """Événement déclenché lorsque le type de catalogue d'un véhicule bascule (SALE <-> RENTAL)."""

    vehicle_id: UUID
    previous_catalog_type: str
    new_catalog_type: str
