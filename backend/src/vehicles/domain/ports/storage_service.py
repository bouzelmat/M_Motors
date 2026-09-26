from abc import ABC, abstractmethod
from typing import Any


class StorageService(ABC):
    """Port déclarant les opérations de stockage de fichiers."""

    @abstractmethod
    async def generate_presigned_post(
        self,
        object_name: str,
        content_type: str,
        max_file_size_bytes: int,
        expiration: int = 3600,
    ) -> dict[str, Any]:
        """Génère une URL pré-signée POST avec contrainte stricte de taille S3 (content-length-range)."""
        pass

    @abstractmethod
    async def object_exists(self, object_name: str) -> bool:
        """Return whether an object exists in the configured storage."""
        pass

    @abstractmethod
    async def get_object_url(self, object_name: str) -> str:
        """Return a URL that can be used to read an uploaded object."""
        pass
