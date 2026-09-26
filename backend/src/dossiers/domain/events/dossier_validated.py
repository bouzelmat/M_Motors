"""Événement déclenché lorsqu'un dossier est validé par un administrateur."""

from dataclasses import dataclass
from uuid import UUID
from src.shared.domain.events.domain_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class DossierValidated(DomainEvent):
    """Événement émis après la validation d'un dossier."""

    dossier_id: UUID
    admin_id: UUID
    comment: str | None = None
