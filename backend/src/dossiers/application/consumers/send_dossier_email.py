"""Consommateurs de notification e-mail pour les événements de dossier.

MVP : journalisation structurée en lieu et place d'un véritable envoi d'e-mail.
"""

import logging

from src.dossiers.domain.events.documents_requested import DocumentsRequested
from src.dossiers.domain.events.dossier_rejected import DossierRejected
from src.dossiers.domain.events.dossier_validated import DossierValidated

logger = logging.getLogger(__name__)


class SendDossierValidatedEmailConsumer:
    """Journalise la notification de validation d'un dossier."""

    async def handle(self, event: DossierValidated) -> None:
        """Log structuré de la validation du dossier."""
        logger.info(
            "EMAIL [DossierValidated] dossier_id=%s admin_id=%s comment=%s",
            event.dossier_id,
            event.admin_id,
            event.comment,
        )


class SendDossierRejectedEmailConsumer:
    """Journalise la notification de rejet d'un dossier."""

    async def handle(self, event: DossierRejected) -> None:
        """Log structuré du rejet du dossier."""
        logger.info(
            "EMAIL [DossierRejected] dossier_id=%s admin_id=%s reason=%s",
            event.dossier_id,
            event.admin_id,
            event.reason,
        )


class SendDocumentsRequestedEmailConsumer:
    """Journalise la notification de demande de documents complémentaires."""

    async def handle(self, event: DocumentsRequested) -> None:
        """Log structuré de la demande de documents."""
        logger.info(
            "EMAIL [DocumentsRequested] dossier_id=%s admin_id=%s document_types=%s",
            event.dossier_id,
            event.admin_id,
            event.document_types,
        )
