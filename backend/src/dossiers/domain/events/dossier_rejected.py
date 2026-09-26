"""Événement déclenché lorsqu'un dossier est rejeté par un administrateur."""

from dataclasses import dataclass
from uuid import UUID
from src.shared.domain.events.domain_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class DossierRejected(DomainEvent):
    """Événement émis après le rejet d'un dossier."""

    dossier_id: UUID
    admin_id: UUID
    reason: str
