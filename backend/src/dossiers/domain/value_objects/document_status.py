"""Objet de valeur représentant le statut d'un document justificatif."""

from enum import Enum


class DocumentStatus(str, Enum):
    """Statuts du cycle de vie d'un document justificatif."""

    PENDING = "PENDING"
    UPLOADED = "UPLOADED"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    PENDING_PURGE = "PENDING_PURGE"
    PURGED = "PURGED"
