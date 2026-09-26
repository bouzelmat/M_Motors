"""Événement déclenché après la purge intégrale des documents d'un dossier rejeté."""

from dataclasses import dataclass
from uuid import UUID

from src.shared.domain.events.domain_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class DossierPurged(DomainEvent):
    """Événement émis lorsque toutes les pièces d'un dossier rejeté ont été purgées."""

    dossier_id: UUID
