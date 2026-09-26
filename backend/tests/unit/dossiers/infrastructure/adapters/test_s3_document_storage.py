"""Tests unitaires pour S3DocumentStorageAdapter (US-304 / US-305)."""

import asyncio
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from src.config import Settings
from src.dossiers.infrastructure.adapters.s3_document_storage import (
    S3DocumentStorageAdapter,
)


@pytest.fixture
def mock_settings() -> Settings:
    """Fixture pour mock Settings."""
    settings = MagicMock(spec=Settings)
    settings.s3_documents_bucket_name = "m-motors-documents"
    settings.aws_region = "eu-west-1"
    settings.aws_access_key_id = "test-access-key"
    settings.aws_secret_access_key = "test-secret-key"
    settings.aws_endpoint_url = "http://localhost:4566"
    return settings


@pytest.fixture
def s3_adapter(mock_settings: Settings) -> S3DocumentStorageAdapter:
    """Fixture pour créer l'adaptateur S3."""
    return S3DocumentStorageAdapter(mock_settings)


class TestGenerateDownloadUrl:
    """Tests pour generate_download_url (US-304 - Critère 7)."""

    @patch("boto3.client")
    def test_generate_download_url_calls_boto3_with_get_object(
        self, mock_boto3, s3_adapter: S3DocumentStorageAdapter
    ) -> None:
        """Vérifie que ClientMethod est 'get_object'."""
        mock_client = MagicMock()
        mock_boto3.return_value = mock_client
        mock_client.generate_presigned_url.return_value = (
            "https://m-motors-documents.s3.amazonaws.com/key?X-Amz-Signature=..."
        )

        s3_key = "dossiers/1234/IDENTITY_CARD/doc.pdf"
        asyncio.run(s3_adapter.generate_download_url(s3_key))

        call_args = mock_client.generate_presigned_url.call_args
        assert call_args[1]["ClientMethod"] == "get_object"

    @patch("boto3.client")
    def test_generate_download_url_uses_correct_bucket(
        self, mock_boto3, s3_adapter: S3DocumentStorageAdapter
    ) -> None:
        """Vérifie que Bucket est 'm-motors-documents'."""
        mock_client = MagicMock()
        mock_boto3.return_value = mock_client
        mock_client.generate_presigned_url.return_value = (
            "https://m-motors-documents.s3.amazonaws.com/key?X-Amz-Signature=..."
        )

        s3_key = "test-key"
        asyncio.run(s3_adapter.generate_download_url(s3_key))

        call_args = mock_client.generate_presigned_url.call_args
        assert call_args[1]["Params"]["Bucket"] == "m-motors-documents"

    @patch("boto3.client")
    def test_generate_download_url_uses_correct_key(
        self, mock_boto3, s3_adapter: S3DocumentStorageAdapter
    ) -> None:
        """Vérifie que Key correspond à s3_key."""
        mock_client = MagicMock()
        mock_boto3.return_value = mock_client
        mock_client.generate_presigned_url.return_value = (
            "https://m-motors-documents.s3.amazonaws.com/key?X-Amz-Signature=..."
        )

        s3_key = "dossiers/1234/IDENTITY_CARD/doc.pdf"
        asyncio.run(s3_adapter.generate_download_url(s3_key))

        call_args = mock_client.generate_presigned_url.call_args
        assert call_args[1]["Params"]["Key"] == s3_key

    @patch("boto3.client")
    def test_generate_download_url_default_expires_in(
        self, mock_boto3, s3_adapter: S3DocumentStorageAdapter
    ) -> None:
        """Vérifie que expires_in défaut est 60 (US-304 - Critère 7)."""
        mock_client = MagicMock()
        mock_boto3.return_value = mock_client
        mock_client.generate_presigned_url.return_value = (
            "https://m-motors-documents.s3.amazonaws.com/key?X-Amz-Signature=..."
        )

        s3_key = "test-key"
        asyncio.run(s3_adapter.generate_download_url(s3_key))

        call_args = mock_client.generate_presigned_url.call_args
        assert call_args[1]["ExpiresIn"] == 60

    @patch("boto3.client")
    def test_generate_download_url_custom_expires_in(
        self, mock_boto3, s3_adapter: S3DocumentStorageAdapter
    ) -> None:
        """Vérifie que expires_in peut être personnalisé."""
        mock_client = MagicMock()
        mock_boto3.return_value = mock_client
        mock_client.generate_presigned_url.return_value = (
            "https://m-motors-documents.s3.amazonaws.com/key?X-Amz-Signature=..."
        )

        s3_key = "test-key"
        custom_expires_in = 120
        asyncio.run(
            s3_adapter.generate_download_url(s3_key, expires_in=custom_expires_in)
        )

        call_args = mock_client.generate_presigned_url.call_args
        assert call_args[1]["ExpiresIn"] == custom_expires_in


class TestDeleteObject:
    """Tests pour delete_object (US-305 - Tâche 3)."""

    @patch("boto3.client")
    def test_delete_object_calls_boto3_with_correct_bucket_and_key(
        self, mock_boto3, s3_adapter: S3DocumentStorageAdapter
    ) -> None:
        """Vérifie que delete_object est appelé avec le bon bucket et la bonne clé."""
        mock_client = MagicMock()
        mock_boto3.return_value = mock_client
        s3_key = "dossiers/1234/IDENTITY_CARD/doc.pdf"

        asyncio.run(s3_adapter.delete_object(s3_key))

        mock_client.delete_object.assert_called_once_with(
            Bucket="m-motors-documents",
            Key=s3_key,
        )

    @patch("boto3.client")
    def test_delete_object_propagates_s3_error(
        self, mock_boto3, s3_adapter: S3DocumentStorageAdapter
    ) -> None:
        """Vérifie que les erreurs ClientError de S3 sont bien propagées."""
        mock_client = MagicMock()
        mock_boto3.return_value = mock_client
        mock_client.delete_object.side_effect = ClientError(
            {"Error": {"Code": "500", "Message": "S3 Internal Error"}},
            "DeleteObject",
        )
        s3_key = "dossiers/1234/IDENTITY_CARD/doc.pdf"

        with pytest.raises(ClientError):
            asyncio.run(s3_adapter.delete_object(s3_key))
