"""Tests unitaires pour le service d'autorisation des documents (US-304)."""

from uuid import uuid4


from src.auth.domain.entities.user import User
from src.auth.domain.value_objects.email import Email
from src.auth.domain.value_objects.role import Role
from src.dossiers.application.services.authorization import can_access_document
from src.dossiers.domain.entities.document import Document
from src.dossiers.domain.entities.dossier import Dossier
from src.dossiers.domain.value_objects.document_type import DocumentType


def mock_user(user_id: str | None = None, role: Role = Role.CLIENT) -> User:
    """Fixture pour créer un utilisateur mocké."""
    return User(
        id=user_id or uuid4(),
        email=Email("test@example.com"),
        hashed_password="hashed_password",
        first_name="Test",
        last_name="User",
        role=role,
    )


def mock_dossier(user_id: str | None = None) -> Dossier:
    """Fixture pour créer un dossier mocké."""
    return Dossier.create(
        user_id=user_id or uuid4(),
        vehicle_id=uuid4(),
    )


def mock_document(dossier_id: str | None = None) -> Document:
    """Fixture pour créer un document mocké."""
    return Document.create_pending(
        dossier_id=dossier_id or uuid4(),
        type=DocumentType.IDENTITY_CARD,
        s3_key="dossiers/test/IDENTITY_CARD/document.pdf",
        original_filename="document.pdf",
        content_type="application/pdf",
        size=1024,
    )


class TestCanAccessDocument:
    """Tests pour can_access_document (US-304 - Critères 3,4,5)."""

    def test_owner_client_can_access(self) -> None:
        """Critère 3 : Un utilisateur authentifié propriétaire du dossier peut demander une URL."""
        user = mock_user(role=Role.CLIENT)
        dossier = mock_dossier(user_id=user.id)
        document = mock_document(dossier_id=dossier.id)
        assert can_access_document(user, document, dossier) is True

    def test_admin_can_access_any_dossier(self) -> None:
        """Critère 4 : Un utilisateur ADMIN peut demander une URL pour tout dossier."""
        admin = mock_user(role=Role.ADMIN)
        user = mock_user(role=Role.CLIENT)
        dossier = mock_dossier(user_id=user.id)
        document = mock_document(dossier_id=dossier.id)
        assert can_access_document(admin, document, dossier) is True

    def test_non_owner_client_cannot_access(self) -> None:
        """Critère 5 : Un utilisateur CLIENT qui n'est pas propriétaire reçoit HTTP 403."""
        user1 = mock_user(role=Role.CLIENT)
        user2 = mock_user(role=Role.CLIENT)
        dossier = mock_dossier(user_id=user1.id)
        document = mock_document(dossier_id=dossier.id)
        assert can_access_document(user2, document, dossier) is False

    def test_document_not_attached_to_dossier_returns_false(self) -> None:
        """Critère 9 : Un document existant mais rattaché à un autre dossier reçoit HTTP 404."""
        user = mock_user(role=Role.CLIENT)
        dossier1 = mock_dossier(user_id=user.id)
        dossier2 = mock_dossier(user_id=user.id)
        document = mock_document(dossier_id=dossier1.id)
        assert can_access_document(user, document, dossier2) is False
