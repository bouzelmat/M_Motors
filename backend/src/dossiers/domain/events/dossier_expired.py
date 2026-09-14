"""Événement déclenché lors de l'expiration automatique d'un dossier DRAFT."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.shared.domain.events.domain_event import DomainEvent


@dataclass(frozen=True)
class DossierExpired(DomainEvent):
    """Événement émis lorsqu'un dossier DRAFT dépasse le délai limite sans soumission."""

    dossier_id: UUID
    vehicle_id: UUID
    expired_at: datetime
