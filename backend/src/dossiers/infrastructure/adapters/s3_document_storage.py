"""Adaptateur S3 pour le stockage des pièces justificatives via boto3."""

import asyncio
from typing import BinaryIO
from uuid import UUID

import boto3
from botocore.config import Config

from src.config import Settings
from src.dossiers.domain.ports.document_storage_port import DocumentStoragePort


class S3DocumentStorageAdapter(DocumentStoragePort):
    """Adaptateur S3 générant des URLs pré-signées pour le stockage de documents."""

    def __init__(self, settings: Settings) -> None:
        self._bucket_name = settings.s3_documents_bucket_name
        self._client = boto3.client(
            "s3",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            endpoint_url=settings.aws_endpoint_url,
            config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
        )

    async def upload(
        self,
        dossier_id: UUID,
        document_type: str,
        file_name: str,
        content: BinaryIO,
    ) -> str:
        """Implémentation synchrone exécutée de manière asynchrone pour l'upload direct."""
        key = f"dossiers/{dossier_id}/{document_type}/{file_name}"
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            lambda: self._client.upload_fileobj(content, self._bucket_name, key),
        )
        return key

    async def generate_upload_url(
        self,
        s3_key: str,
        content_type: str,
        expires_in: int = 300,
    ) -> str:
        """Génère une URL pré-signée PUT pour téléverser un fichier S3."""
        loop = asyncio.get_running_loop()
        url = await loop.run_in_executor(
            None,
            lambda: self._client.generate_presigned_url(
                ClientMethod="put_object",
                Params={
                    "Bucket": self._bucket_name,
                    "Key": s3_key,
                    "ContentType": content_type,
                },
                ExpiresIn=expires_in,
            ),
        )
        return url
