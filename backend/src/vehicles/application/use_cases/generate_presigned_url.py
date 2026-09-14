import mimetypes
import uuid
from typing import Any
from uuid import UUID

from src.vehicles.domain.exceptions import (
    FileSizeExceededError,
    InvalidImageFormatError,
    VehicleNotFoundError,
)
from src.vehicles.domain.ports.storage_service import StorageService
from src.vehicles.domain.ports.vehicle_repository import VehicleRepository

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 Mo
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}


class GeneratePresignedUploadUrlUseCase:
    """Cas d'usage contrôlant l'existence du véhicule, la conformité de l'image et déléguant la signature S3."""

    def __init__(
        self,
        storage_service: StorageService,
        vehicle_repository: VehicleRepository,
    ) -> None:
        self._storage_service = storage_service
        self._vehicle_repository = vehicle_repository

    async def execute(
        self,
        vehicle_id: UUID,
        file_name: str,
        file_size: int,
        content_type: str,
    ) -> dict[str, Any]:
        # 1. Vérification de l'existence du véhicule (Agrégat Métier)
        # Correction : Remplacement de get_by_id par find_by_id conforme au Port du Domaine
        vehicle = await self._vehicle_repository.find_by_id(vehicle_id)
        if not vehicle:
            raise VehicleNotFoundError(vehicle_id=vehicle_id)

        # 2. Validation du Type MIME
        if content_type.lower() not in ALLOWED_MIME_TYPES:
            raise InvalidImageFormatError(content_type=content_type)

        # 3. Validation pré-vol de la taille déclarée
        if file_size > MAX_FILE_SIZE_BYTES:
            raise FileSizeExceededError(size=file_size, max_size=MAX_FILE_SIZE_BYTES)

        # 4. Génération d'un nom d'objet S3 sécurisé (anti-path traversal, anti-collision)
        extension = mimetypes.guess_extension(content_type) or ".jpg"
        if extension == ".jpe":
            extension = ".jpg"

        secure_object_name = f"vehicles/{vehicle_id}/{uuid.uuid4()}{extension}"

        # 5. Délégation de la génération de Presigned POST avec contrainte S3
        return await self._storage_service.generate_presigned_post(
            object_name=secure_object_name,
            content_type=content_type,
            max_file_size_bytes=MAX_FILE_SIZE_BYTES,
        )
