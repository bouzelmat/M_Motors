"""Événement déclenché lorsqu'un administrateur demande des documents complémentaires."""

from dataclasses import dataclass
from uuid import UUID
from src.shared.domain.events.domain_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class DocumentsRequested(DomainEvent):
    """Événement émis après la demande de documents complémentaires."""

    dossier_id: UUID
    admin_id: UUID
    document_types: list[str]
