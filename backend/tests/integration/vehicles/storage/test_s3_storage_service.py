"""Tests d'intégration du service S3 (génération et upload via Moto)."""

import asyncio
import base64
import json

import boto3
import pytest
import requests
from moto import mock_aws

from src.shared.infrastructure.config import get_settings
from src.vehicles.infrastructure.storage.s3_storage_service import S3StorageService

AWS_REGION = "eu-west-3"
S3_BUCKET = "m-motors-photos-test"
OBJECT_KEY = "vehicles/test-vehicle/photo.jpg"
JPEG_CONTENT = (
    b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C"
)


@pytest.fixture
def s3_env(monkeypatch):
    """Configure l'environnement AWS de test et initialise le bucket Moto."""
    monkeypatch.setenv("s3_bucket_name", S3_BUCKET)
    monkeypatch.setenv("aws_access_key_id", "testing")
    monkeypatch.setenv("aws_secret_access_key", "testing")
    monkeypatch.setenv("aws_region", AWS_REGION)
    monkeypatch.setenv("aws_endpoint_url", "")
    monkeypatch.setenv("AWS_ENDPOINT_URL", "")
    get_settings.cache_clear()

    with mock_aws():
        s3 = boto3.client("s3", region_name=AWS_REGION)
        s3.create_bucket(
            Bucket=S3_BUCKET,
            CreateBucketConfiguration={"LocationConstraint": AWS_REGION},
        )
        yield s3


@pytest.mark.asyncio
async def test_generate_presigned_post_returns_signed_fields(s3_env) -> None:
    """Le service doit retourner une URL et une policy signée conforme."""
    service = S3StorageService()

    result = await service.generate_presigned_post(
        object_name=OBJECT_KEY,
        content_type="image/jpeg",
        max_file_size_bytes=10 * 1024 * 1024,
    )

    assert "url" in result
    assert "fields" in result
    assert result["fields"]["key"] == OBJECT_KEY
    assert result["fields"]["Content-Type"] == "image/jpeg"
    assert "policy" in result["fields"]
    assert "x-amz-signature" in result["fields"]

    policy = json.loads(base64.b64decode(result["fields"]["policy"]))
    assert {"bucket": S3_BUCKET} in policy["conditions"]
    assert {"key": OBJECT_KEY} in policy["conditions"]
    assert {"Content-Type": "image/jpeg"} in policy["conditions"]
    assert ["content-length-range", 1, 10 * 1024 * 1024] in policy["conditions"]


def test_presigned_post_upload_succeeds_with_moto(s3_env) -> None:
    """L'upload multipart via requests doit réussir dans le contexte Moto."""
    service = S3StorageService()
    result = asyncio.run(
        service.generate_presigned_post(
            object_name=OBJECT_KEY,
            content_type="image/jpeg",
            max_file_size_bytes=10 * 1024 * 1024,
        )
    )

    upload_fields = {key: (None, str(value)) for key, value in result["fields"].items()}
    upload_fields["file"] = ("photo.jpg", JPEG_CONTENT, "image/jpeg")

    # requests est intercepté par Moto ; httpx sort du mock et cible AWS réel.
    response = requests.post(result["url"], files=upload_fields, timeout=10)

    assert response.status_code in (200, 204)

    objects = s3_env.list_objects_v2(Bucket=S3_BUCKET, Prefix=OBJECT_KEY)
    assert objects["KeyCount"] == 1
    assert objects["Contents"][0]["Key"] == OBJECT_KEY
