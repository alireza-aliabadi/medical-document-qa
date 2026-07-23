"""Celery application configuration."""

from backend.core.config import get_settings
from celery import Celery

settings = get_settings()

celery_app = Celery(
    "medical_kb",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["backend.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
