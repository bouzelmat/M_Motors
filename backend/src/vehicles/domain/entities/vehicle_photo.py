"""Informations métier d'une photo associée à un véhicule."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class VehiclePhoto:
    """Métadonnées d'une photo confirmée dans le catalogue véhicule."""

    id: UUID
    vehicle_id: UUID
    object_key: str
    is_primary: bool
    created_at: datetime
    uploaded_at: datetime | None
