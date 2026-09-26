"""Query applicative pour la consultation du détail d'un dossier côté admin."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class GetAdminDossierDetailQuery:
    """Paramètres d'entrée de la requête de détail d'un dossier pour l'administration."""

    dossier_id: UUID
