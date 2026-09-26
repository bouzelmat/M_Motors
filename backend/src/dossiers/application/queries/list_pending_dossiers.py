"""Query applicative pour la consultation des dossiers en attente."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ListPendingDossiersQuery:
    """Paramètres d'entrée de la requête de listing des dossiers en attente."""

    sort_by: str = "submitted_at"
