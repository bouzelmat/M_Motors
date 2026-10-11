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
    submitted_at: datetime | None = None
    rejected_at: datetime | None = None
    comment: str | None = None
    rejection_reason: str | None = None
    requested_document_types: list[str] | None = None
    validated_by_admin_id: UUID | None = None
    rejected_by_admin_id: UUID | None = None
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
            submitted_at=None,
            rejected_at=None,
            comment=None,
            rejection_reason=None,
            requested_document_types=None,
            validated_by_admin_id=None,
            rejected_by_admin_id=None,
            created_at=now,
            updated_at=now,
        )

    def is_owned_by(self, user_id: UUID) -> bool:
        """Indique si le dossier appartient à l'utilisateur fourni."""
        return self.user_id == user_id

    def is_rejected_since(
        self, days: int, reference_date: datetime | None = None
    ) -> bool:
        """Vérifie si le dossier est au statut REJECTED depuis au moins N jours."""
        if self.status != DossierStatus.REJECTED or self.rejected_at is None:
            return False
        now = reference_date or datetime.now(timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        rejected_at_utc = self.rejected_at
        if rejected_at_utc.tzinfo is None:
            rejected_at_utc = rejected_at_utc.replace(tzinfo=timezone.utc)
        delta = now - rejected_at_utc
        return delta.days >= days

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

    def submit(self, now: datetime | None = None) -> "Dossier":
        """Soumet un brouillon ou un dossier complété après demande de pièces."""
        if self.status not in (DossierStatus.DRAFT, DossierStatus.DOCUMENTS_PENDING):
            raise DomainError(
                f"Impossible de soumettre un dossier au statut {self.status.value}."
            )
        current_time = now or datetime.now(timezone.utc)
        return replace(
            self,
            status=DossierStatus.SUBMITTED,
            submitted_at=current_time,
            requested_document_types=None,
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

    def cancel(self, now: datetime | None = None) -> "Dossier":
        """Annule un dossier encore en préparation."""
        if self.status != DossierStatus.DRAFT:
            raise DomainError(
                f"Impossible d'annuler un dossier au statut {self.status.value}."
            )
        current_time = now or datetime.now(timezone.utc)
        return replace(
            self,
            status=DossierStatus.CANCELLED,
            updated_at=current_time,
        )

    def approve(
        self,
        admin_id: UUID,
        comment: str | None = None,
        now: datetime | None = None,
    ) -> "Dossier":
        """Valide le dossier depuis le statut SUBMITTED."""
        if self.status != DossierStatus.SUBMITTED:
            raise DomainError(
                f"Impossible de valider un dossier au statut {self.status.value}."
            )
        current_time = now or datetime.now(timezone.utc)
        return replace(
            self,
            status=DossierStatus.VALIDATED,
            comment=comment,
            validated_by_admin_id=admin_id,
            updated_at=current_time,
        )

    def reject(
        self,
        admin_id: UUID,
        reason: str,
        now: datetime | None = None,
    ) -> "Dossier":
        """Rejette le dossier depuis le statut SUBMITTED."""
        if self.status != DossierStatus.SUBMITTED:
            raise DomainError(
                f"Impossible de rejeter un dossier au statut {self.status.value}."
            )
        if not reason or not reason.strip():
            raise DomainError("Le motif de rejet ne peut pas être vide.")
        current_time = now or datetime.now(timezone.utc)
        return replace(
            self,
            status=DossierStatus.REJECTED,
            rejection_reason=reason.strip(),
            rejected_by_admin_id=admin_id,
            rejected_at=current_time,
            updated_at=current_time,
        )

    def request_documents(
        self,
        document_types: list[str],
        now: datetime | None = None,
    ) -> "Dossier":
        """Demande des documents complémentaires depuis SUBMITTED ou DOCUMENTS_PENDING."""
        if self.status not in (
            DossierStatus.SUBMITTED,
            DossierStatus.DOCUMENTS_PENDING,
        ):
            raise DomainError(
                f"Impossible de demander des documents pour un dossier au statut {self.status.value}."
            )
        if not document_types:
            raise DomainError("La liste des documents demandés ne peut pas être vide.")
        current_time = now or datetime.now(timezone.utc)
        return replace(
            self,
            status=DossierStatus.DOCUMENTS_PENDING,
            requested_document_types=document_types,
            updated_at=current_time,
        )
