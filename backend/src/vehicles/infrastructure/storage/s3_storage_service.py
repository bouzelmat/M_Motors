from typing import Any

try:
    import boto3
    from botocore.config import Config

    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

from src.config import get_settings
from src.vehicles.domain.ports.storage_service import StorageService


class S3StorageService(StorageService):
    """Adaptateur S3 implémentant le port StorageService via boto3."""

    def __init__(self) -> None:
        if not BOTO3_AVAILABLE:
            raise ImportError(
                "boto3 is not installed. S3StorageService requires boto3."
            )
        settings = get_settings()
        self._bucket_name = settings.s3_bucket_name

        client_kwargs = {
            "service_name": "s3",
            "region_name": settings.aws_region,
            "aws_access_key_id": settings.aws_access_key_id,
            "aws_secret_access_key": settings.aws_secret_access_key,
            "config": Config(signature_version="s3v4"),
        }
        if settings.aws_endpoint_url:
            client_kwargs["endpoint_url"] = settings.aws_endpoint_url

        self._s3_client = boto3.client(**client_kwargs)
        self._presigning_client = self._s3_client
        if settings.aws_public_endpoint_url:
            presigning_kwargs = {
                **client_kwargs,
                "endpoint_url": settings.aws_public_endpoint_url,
            }
            self._presigning_client = boto3.client(**presigning_kwargs)

    async def generate_presigned_post(
        self,
        object_name: str,
        content_type: str,
        max_file_size_bytes: int,
        expiration: int = 3600,
    ) -> dict[str, Any]:
        """
        Génère les champs et l'URL pour un HTTP POST direct vers S3.
        Incorpore la condition de taille 'content-length-range' vérifiée physiquement par AWS S3.
        """
        conditions = [
            {"bucket": self._bucket_name},
            {"key": object_name},
            {"Content-Type": content_type},
            [
                "content-length-range",
                1,
                max_file_size_bytes,
            ],  # Force S3 à rejeter si > max_file_size_bytes
        ]

        fields = {
            "Content-Type": content_type,
        }

        # generate_presigned_post applique les conditions dans la politique signée (Policy Document)
        response = self._presigning_client.generate_presigned_post(
            Bucket=self._bucket_name,
            Key=object_name,
            Fields=fields,
            Conditions=conditions,
            ExpiresIn=expiration,
        )
        return response

    async def object_exists(self, object_name: str) -> bool:
        try:
            self._s3_client.head_object(Bucket=self._bucket_name, Key=object_name)
        except self._s3_client.exceptions.ClientError as exc:
            if exc.response.get("Error", {}).get("Code") in {"404", "NoSuchKey"}:
                return False
            raise
        return True

    async def get_object_url(self, object_name: str) -> str:
        return self._presigning_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket_name, "Key": object_name},
            ExpiresIn=3600,
        )

    async def delete_object(self, object_name: str) -> None:
        self._s3_client.delete_object(Bucket=self._bucket_name, Key=object_name)
