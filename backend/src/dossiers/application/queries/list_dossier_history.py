"""Requête applicative pour consulter l'historique des dossiers clôturés."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ListDossierHistoryQuery:
    """Requête de lecture des dossiers archivés."""
