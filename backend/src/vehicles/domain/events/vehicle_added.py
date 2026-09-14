"""Événement de domaine émis lors de l'ajout d'un nouveau véhicule."""

from dataclasses import dataclass
from uuid import UUID

from src.shared.domain.events.domain_event import DomainEvent


@dataclass(frozen=True)
class VehicleAdded(DomainEvent):
    """Événement déclenché après la création d'un véhicule dans le catalogue."""

    vehicle_id: UUID
    brand: str
    model: str
    catalog_type: str
