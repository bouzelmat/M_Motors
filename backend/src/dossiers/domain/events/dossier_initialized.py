"""Événement de domaine émis lors de l'initialisation d'un dossier."""

from dataclasses import dataclass
from uuid import UUID

from src.shared.domain.events.domain_event import DomainEvent


@dataclass(frozen=True)
class DossierInitialized(DomainEvent):
    """Événement déclenché après la création initiale d'un dossier au statut DRAFT."""

    dossier_id: UUID
    user_id: UUID
    vehicle_id: UUID