"""Constantes applicatives liées à la gestion des dossiers."""

from src.dossiers.domain.value_objects.dossier_status import DossierStatus

PENDING_STATUSES = frozenset(
    {
        DossierStatus.SUBMITTED,
        DossierStatus.DOCUMENTS_PENDING,
    }
)

HISTORICAL_STATUSES = frozenset(
    {
        DossierStatus.VALIDATED,
        DossierStatus.REJECTED,
        DossierStatus.EXPIRED,
        DossierStatus.CANCELLED,
    }
)
