"""S3-compatible object storage (MinIO / AIStor)."""

import logging
from uuid import uuid4

import boto3
from backend.core.config import Settings, get_settings
from botocore.client import Config

logger = logging.getLogger(__name__)


class StorageService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._client = boto3.client(
            "s3",
            endpoint_url=self.settings.s3_endpoint,
            aws_access_key_id=self.settings.s3_access_key,
            aws_secret_access_key=self.settings.s3_secret_key,
            region_name=self.settings.s3_region,
            config=Config(signature_version="s3v4"),
        )
        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        try:
            self._client.head_bucket(Bucket=self.settings.s3_bucket)
        except Exception:
            try:
                self._client.create_bucket(Bucket=self.settings.s3_bucket)
                logger.info("Created bucket %s", self.settings.s3_bucket)
            except Exception as exc:
                logger.warning("Could not create bucket: %s", exc)

    def upload_bytes(self, data: bytes, filename: str, content_type: str) -> str:
        key = f"documents/{uuid4()}/{filename}"
        self._client.put_object(
            Bucket=self.settings.s3_bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        return key

    def download_bytes(self, key: str) -> bytes:
        response = self._client.get_object(Bucket=self.settings.s3_bucket, Key=key)
        return response["Body"].read()

    def delete_object(self, key: str) -> None:
        self._client.delete_object(Bucket=self.settings.s3_bucket, Key=key)
