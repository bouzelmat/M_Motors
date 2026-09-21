"""Schémas Pydantic v2 pour les requêtes et réponses de l'API Dossiers."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.dossiers.domain.value_objects.dossier_status import DossierStatus


class TradeInRequest(BaseModel):
    """Payload pour la demande de reprise véhicule."""

    registration: str = Field(..., min_length=1)
    mileage: int = Field(..., ge=0)
    brand: str | None = None
    model: str | None = None


class FinancingPlanRequest(BaseModel):
    """Payload pour la demande de plan de financement."""

    down_payment: Decimal = Field(..., ge=0)
    duration_months: int = Field(..., gt=0)
    monthly_payment: Decimal = Field(..., ge=0)


class CreateDossierRequest(BaseModel):
    """Payload de création d'un dossier."""

    vehicle_id: UUID
    trade_in: TradeInRequest | None = None
    financing_plan: FinancingPlanRequest | None = None


class DossierResponse(BaseModel):
    """Représentation d'un dossier retournée par l'API."""

    dossier_id: UUID = Field(..., alias="id")
    vehicle_id: UUID
    status: DossierStatus

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
