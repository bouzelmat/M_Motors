"""Entité représentant un dossier de demande (achat ou location)."""

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.dossiers.domain.value_objects.dossier_status import DossierStatus
from src.dossiers.domain.value_objects.financing_plan import FinancingPlan
from src.dossiers.domain.value_objects.trade_in import TradeIn
from src.shared.domain.entity import Entity
from src.shared.domain.exceptions import DomainError


@dataclass(frozen=True)
class Dossier(Entity):
    id: UUID
    user_id: UUID
    vehicle_id: UUID
    status: DossierStatus
    trade_in: TradeIn | None = None
    financing_plan: FinancingPlan | None = None
    upload_started_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        user_id: UUID,
        vehicle_id: UUID,
        trade_in: TradeIn | None = None,
        financing_plan: FinancingPlan | None = None,
    ) -> "Dossier":
        """Crée un dossier brouillon associé à un utilisateur et un véhicule."""
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid4(),
            user_id=user_id,
            vehicle_id=vehicle_id,
            status=DossierStatus.DRAFT,
            trade_in=trade_in,
            financing_plan=financing_plan,
            upload_started_at=None,
            created_at=now,
            updated_at=now,
        )

    def is_owned_by(self, user_id: UUID) -> bool:
        """Indique si le dossier appartient à l'utilisateur fourni."""
        return self.user_id == user_id

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