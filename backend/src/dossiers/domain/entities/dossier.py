"""Entité représentant un dossier de demande (achat ou location)."""

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from uuid import UUID

from src.dossiers.domain.value_objects.dossier_status import DossierStatus
from src.shared.domain.entity import Entity
from src.shared.domain.exceptions import DomainError


@dataclass(frozen=True)
class Dossier(Entity):
    id: UUID
    user_id: UUID
    vehicle_id: UUID
    status: DossierStatus
    upload_started_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def mark_upload_started(self, now: datetime | None = None) -> "Dossier":
        """Positionne l'horodatage du premier téléversement s'il n'est pas déjà défini."""
        if self.upload_started_at is not None:
            return self

        current_time = now or datetime.now(timezone.utc)
        return replace(
            self,
            upload_started_at=current_time,
            updated_at=current_time,
        )

    def expire(self, now: datetime | None = None) -> "Dossier":
        """Fait transiter le dossier vers le statut EXPIRED."""
        if self.status != DossierStatus.DRAFT:
            raise DomainError(
                f"Impossible d'expirer un dossier au statut {self.status.value}."
            )

        current_time = now or datetime.now(timezone.utc)
        return replace(
            self,
            status=DossierStatus.EXPIRED,
            updated_at=current_time,
        )
