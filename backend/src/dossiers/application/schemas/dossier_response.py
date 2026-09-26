"""Schémas Pydantic pour les réponses de l'API dossiers."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from src.dossiers.domain.value_objects.dossier_status import DossierStatus


class DocumentListItemResponse(BaseModel):
    """Représentation JSON d'un document associé à un dossier."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    type: str
    status: str
    original_filename: str
    content_type: str
    size: int
    created_at: datetime
    uploaded_at: datetime | None = None


class FinancingPlanResponse(BaseModel):
    """Représentation JSON d'un plan de financement."""

    model_config = ConfigDict(from_attributes=True)

    down_payment: Decimal
    duration_months: int
    monthly_payment: Decimal


class TradeInResponse(BaseModel):
    """Représentation JSON d'un véhicule de reprise."""

    model_config = ConfigDict(from_attributes=True)

    registration: str
    mileage: int
    brand: str | None = None
    model: str | None = None
    estimated_value: Decimal | None = None


class PendingDossierResponse(BaseModel):
    """Représentation JSON d'un dossier en attente pour le back-office."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    client_email: EmailStr
    vehicle_id: UUID
    vehicle_brand: str
    vehicle_model: str
    status: DossierStatus
    submitted_at: datetime | None
    created_at: datetime
    updated_at: datetime


class AdminDossierDetailResponse(BaseModel):
    """Représentation JSON détaillée d'un dossier pour le back-office."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    client_email: EmailStr
    vehicle_id: UUID
    vehicle_brand: str
    vehicle_model: str
    vehicle_price: Decimal | None = None
    status: DossierStatus
    submitted_at: datetime | None = None
    financing_plan: FinancingPlanResponse | None = None
    trade_in: TradeInResponse | None = None
    documents: list[DocumentListItemResponse]
    comment: str | None = None
    rejection_reason: str | None = None
    requested_document_types: list[str] | None = None
    rejected_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
