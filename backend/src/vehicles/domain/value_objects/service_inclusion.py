"""Value object representing a vehicle service and its inclusion status."""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from src.vehicles.domain.value_objects.service_category import ServiceCategory


@dataclass(frozen=True)
class ServiceInclusion:
    """Represent a service available for a vehicle."""

    service_id: UUID
    name: str
    monthly_cost: Decimal
    category: ServiceCategory
    included: bool
