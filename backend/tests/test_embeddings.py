"""Tests for embedding service."""

import pytest
from backend.services.embeddings import EmbeddingService


def test_mock_embeddings_deterministic():
    service = EmbeddingService()
    service.settings.use_mock_embeddings = True
    v1 = service.embed_query("diabetes treatment")
    v2 = service.embed_query("diabetes treatment")
    assert v1 == v2
    assert len(v1) == service.settings.embedding_dimension


def test_cosine_similarity():
    a = [1.0, 0.0]
    b = [1.0, 0.0]
    assert EmbeddingService.cosine_similarity(a, b) == pytest.approx(1.0)
