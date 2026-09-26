"""Objet de valeur représentant le statut d'un dossier de demande."""

from enum import Enum


class DossierStatus(str, Enum):
    """Statuts du cycle de vie d'un dossier."""

    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    DOCUMENTS_PENDING = "DOCUMENTS_PENDING"
