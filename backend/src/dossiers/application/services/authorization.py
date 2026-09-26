"""Service d'autorisation pour l'accès aux documents des dossiers."""

from src.auth.domain.entities.user import User
from src.auth.domain.value_objects.role import Role
from src.dossiers.domain.entities.document import Document
from src.dossiers.domain.entities.dossier import Dossier


def can_access_document(user: User, document: Document, dossier: Dossier) -> bool:
    """Indique si l'utilisateur peut consulter le document du dossier.

    Args:
        user: L'utilisateur authentifié.
        document: Le document à consulter.
        dossier: Le dossier associé au document.

    Returns:
        True si l'utilisateur a le droit d'accéder au document, False sinon.

    Règles (US-304) :
        1. Le document doit être rattaché au dossier (document.dossier_id == dossier.id).
        2. L'utilisateur doit être propriétaire du dossier (dossier.is_owned_by(user.id))
           OU avoir le rôle ADMIN (user.role == Role.ADMIN).
    """
    if document.dossier_id != dossier.id:
        return False
    return dossier.is_owned_by(user.id) or user.role == Role.ADMIN
