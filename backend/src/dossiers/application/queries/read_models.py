"""Read models pour les queries de dossiers."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.dossiers.domain.value_objects.dossier_status import DossierStatus
from src.dossiers.domain.value_objects.financing_plan import FinancingPlan
from src.dossiers.domain.value_objects.trade_in import TradeIn


@dataclass(frozen=True)
class PendingDossierReadModel:
    """Read model pour la liste des dossiers en attente."""

    id: UUID
    user_id: UUID
    client_email: str
    vehicle_id: UUID
    vehicle_brand: str
    vehicle_model: str
    status: DossierStatus
    submitted_at: datetime | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class DocumentReadModel:
    """Read model pour un document associé à un dossier."""

    id: UUID
    type: str
    status: str
    original_filename: str
    content_type: str
    size: int
    created_at: datetime
    uploaded_at: datetime | None = None


@dataclass(frozen=True)
class AdminDossierDetailReadModel:
    """Read model pour le détail d'un dossier côté administrateur."""

    id: UUID
    user_id: UUID
    client_email: str
    vehicle_id: UUID
    vehicle_brand: str
    vehicle_model: str
    vehicle_price: Decimal | None
    status: DossierStatus
    submitted_at: datetime | None
    financing_plan: FinancingPlan | None
    trade_in: TradeIn | None
    documents: list[DocumentReadModel] = field(default_factory=list)
    comment: str | None = None
    rejection_reason: str | None = None
    requested_document_types: list[str] | None = None
    rejected_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now())
    updated_at: datetime = field(default_factory=lambda: datetime.now())
