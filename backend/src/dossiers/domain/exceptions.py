"""Exceptions métier du contexte dossiers."""

from __future__ import annotations

from uuid import UUID

from src.shared.domain.exceptions import (
    ConflictError,
    DomainError,
    ForbiddenError,
    NotFoundError,
)

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


class DossierDomainException(DomainError):
    """Base des erreurs métier du contexte dossiers."""


class VehicleNotFoundException(NotFoundError, DossierDomainException):
    """Levée quand le véhicule référencé n'existe pas."""

    def __init__(self, vehicle_id: UUID) -> None:
        self.vehicle_id = vehicle_id
        super().__init__(f"Véhicule introuvable : {vehicle_id}")


class VehicleNotAvailableException(ConflictError, DossierDomainException):
    """Levée quand le véhicule référencé n'est pas disponible."""

    def __init__(self, vehicle_id: UUID) -> None:
        self.vehicle_id = vehicle_id
        super().__init__(f"Véhicule non disponible pour un dossier : {vehicle_id}")


class DossierNotFoundException(NotFoundError, DossierDomainException):
    """Levée quand le dossier demandé n'existe pas."""

    def __init__(self, dossier_id: UUID | str) -> None:
        self.dossier_id = dossier_id
        super().__init__(f"Dossier introuvable : {dossier_id}")


class DocumentNotFoundException(NotFoundError, DossierDomainException):
    """Levée quand le document demandé n'existe pas."""

    def __init__(self, document_id: UUID | str) -> None:
        self.document_id = document_id
        super().__init__(f"Document introuvable : {document_id}")


class DossierAccessDeniedException(ForbiddenError, DossierDomainException):
    """Levée lors d'un accès non autorisé à un dossier."""

    def __init__(self, message: str = "Accès refusé au dossier.") -> None:
        super().__init__(message)


class InvalidDocumentStateException(ConflictError, DossierDomainException):
    """Levée quand l'état d'un document interdit l'action demandée."""

    def __init__(self, message: str = "État du document invalide.") -> None:
        super().__init__(message)


class DocumentPendingPurgeNotAllowedException(InvalidDocumentStateException):
    """Levée lorsqu'un document ne peut pas passer en attente de purge."""

    def __init__(self, current_status: str) -> None:
        super().__init__(
            f"Impossible de passer en attente de purge un document au statut '{current_status}'."
        )


class DocumentPurgeNotAllowedException(InvalidDocumentStateException):
    """Levée lorsqu'un document ne peut pas être purgé."""

    def __init__(self, current_status: str) -> None:
        super().__init__(
            f"Impossible de purger un document au statut '{current_status}'. "
            "Seuls les documents 'PENDING_PURGE' peuvent être purgés."
        )
