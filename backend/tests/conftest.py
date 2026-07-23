"""Fix conftest import order."""

import os

import pytest
from backend.core.config import get_settings


@pytest.fixture(scope="session", autouse=True)
def test_env():
    os.environ["APP_ENV"] = "test"
    os.environ["USE_MOCK_EMBEDDINGS"] = "true"
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
