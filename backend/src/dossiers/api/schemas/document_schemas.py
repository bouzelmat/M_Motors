"""Schémas Pydantic v2 pour la gestion des pièces justificatives."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.dossiers.domain.value_objects.document_status import DocumentStatus
from src.dossiers.domain.value_objects.document_type import DocumentType

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
}

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 Mo en octets


class PresignedUrlRequest(BaseModel):
    """Payload de demande d'URL pré-signée pour l'upload d'un document."""

    document_type: DocumentType
    filename: str = Field(..., min_length=1, max_length=255)
    content_type: str = Field(...)
    size: int = Field(..., gt=0)

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, v: str) -> str:
        cleaned_type = v.lower().strip()
        if cleaned_type not in ALLOWED_CONTENT_TYPES:
            raise ValueError(
                f"Type de fichier non autorisé '{v}'. Types acceptés : PDF, JPEG, PNG."
            )
        return cleaned_type

    @field_validator("filename")
    @classmethod
    def validate_extension(cls, v: str) -> str:
        lower_filename = v.lower()
        if not any(lower_filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
            raise ValueError(
                "Extension de fichier non autorisée. Seules les extensions .pdf, .jpg, .jpeg, .png sont acceptées."
            )
        return v

    @field_validator("size")
    @classmethod
    def validate_size(cls, v: int) -> int:
        if v > MAX_FILE_SIZE:
            raise ValueError(
                "La taille du fichier dépasse la limite maximale autorisée de 10 Mo."
            )
        return v


class PresignedUrlResponse(BaseModel):
    """Réponse contenant l'URL pré-signée et l'identifiant du document généré."""

    document_id: UUID
    upload_url: str
    s3_key: str


class DocumentConfirmResponse(BaseModel):
    """Réponse lors de la confirmation du téléversement d'un document."""

    document_id: UUID = Field(validation_alias="id")
    status: DocumentStatus
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentListItemResponse(BaseModel):
    """Représentation d'un document dans la liste des pièces d'un dossier."""

    id: UUID
    type: DocumentType
    status: DocumentStatus
    original_filename: str
    content_type: str
    size: int
    created_at: datetime
    uploaded_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ViewUrlResponse(BaseModel):
    """Réponse contenant une URL temporaire de consultation (US-304 - Contrat API)."""

    url: str
    expires_in: int
