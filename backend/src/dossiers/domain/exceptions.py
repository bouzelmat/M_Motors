"""Exceptions du domaine `dossiers`.

Ces exceptions représentent des violations de règles métier détectées lors
du traitement d'un dossier client. Elles sont pures (zéro dépendance
framework) et ne doivent jamais fuiter telles quelles vers le client.
"""

from __future__ import annotations

from uuid import UUID

__all__ = [
    "DossierDomainException",
    "VehicleNotFoundException",
    "VehicleNotAvailableException",
    "DossierNotFoundException",
    "DocumentNotFoundException",
    "DossierAccessDeniedException",
    "InvalidDocumentStateException",
    "DocumentPendingPurgeNotAllowedException",
    "DocumentPurgeNotAllowedException",
]


class DossierDomainException(Exception):
    """Exception de base pour toute règle métier violée dans le contexte `dossiers`."""


class VehicleNotFoundException(DossierDomainException):
    """Levée quand le véhicule référencé par un dossier n'existe pas dans le catalogue."""

    def __init__(self, vehicle_id: UUID) -> None:
        self.vehicle_id = vehicle_id
        super().__init__(f"Véhicule introuvable : {vehicle_id}")


class VehicleNotAvailableException(DossierDomainException):
    """Levée quand le véhicule référencé par un dossier existe mais n'est pas disponible."""

    def __init__(self, vehicle_id: UUID) -> None:
        self.vehicle_id = vehicle_id
        super().__init__(f"Véhicule non disponible pour un dossier : {vehicle_id}")


class DossierNotFoundException(DossierDomainException):
    """Levée quand le dossier demandé n'existe pas."""

    def __init__(self, dossier_id: UUID | str) -> None:
        self.dossier_id = dossier_id
        super().__init__(f"Dossier introuvable : {dossier_id}")


class DocumentNotFoundException(DossierDomainException):
    """Levée quand un document demandé n'existe pas."""

    def __init__(self, document_id: UUID | str) -> None:
        self.document_id = document_id
        super().__init__(f"Document introuvable : {document_id}")


class DossierAccessDeniedException(DossierDomainException):
    """Levée lorsqu'un utilisateur tente d'accéder à un dossier sans privilèges."""

    def __init__(self, message: str = "Accès refusé au dossier.") -> None:
        super().__init__(message)


class InvalidDocumentStateException(DossierDomainException):
    """Levée quand un document se trouve dans un état incompatible avec l'action."""

    def __init__(self, message: str = "État du document invalide.") -> None:
        super().__init__(message)


class DocumentPendingPurgeNotAllowedException(InvalidDocumentStateException):
    """Levée lorsqu'un document ne peut pas passer au statut PENDING_PURGE."""

    def __init__(self, current_status: str) -> None:
        super().__init__(
            f"Impossible de passer en attente de purge un document au statut '{current_status}'."
        )


class DocumentPurgeNotAllowedException(InvalidDocumentStateException):
    """Levée lorsqu'un document ne peut pas passer au statut PURGED."""

    def __init__(self, current_status: str) -> None:
        super().__init__(
            f"Impossible de purger un document au statut '{current_status}'. Seuls les documents 'PENDING_PURGE' peuvent être purgés."
        )
