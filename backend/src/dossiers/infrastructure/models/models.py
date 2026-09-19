"""Module d'exportation centralisée des modèles ORM du Bounded Context dossiers."""

from src.dossiers.infrastructure.models.document_model import DocumentModel
from src.dossiers.infrastructure.models.dossier_model import DossierModel
from src.dossiers.infrastructure.models.dossier_service_model import DossierServiceModel
from src.dossiers.infrastructure.models.financing_plan_model import FinancingPlanModel
from src.dossiers.infrastructure.models.trade_in_model import TradeInModel

__all__ = [
    "DossierModel",
    "FinancingPlanModel",
    "TradeInModel",
    "DossierServiceModel",
    "DocumentModel",
]