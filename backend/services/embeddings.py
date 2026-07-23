"""Embedding generation with optional mock mode for development."""

import hashlib
import logging
import math
from typing import Any, cast

import numpy as np
from backend.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._model = None

    def _load_model(self) -> object | None:
        if self._model is not None:
            return self._model
        if self.settings.use_mock_embeddings:
            return None
        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.settings.embedding_model)
            logger.info("Loaded embedding model %s", self.settings.embedding_model)
            return self._model
        except ImportError:
            logger.warning("sentence-transformers not installed; using mock embeddings")
            return None

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        model = self._load_model()
        if model is None:
            return [self._mock_embedding(text) for text in texts]
        vectors = cast(Any, model).encode(texts, normalize_embeddings=True)
        return [v.tolist() for v in vectors]

    def embed_query(self, query: str) -> list[float]:
        return self.embed_texts([query])[0]

    def _mock_embedding(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode()).digest()
        dim = self.settings.embedding_dimension
        values = [digest[i % len(digest)] / 255.0 for i in range(dim)]
        norm = math.sqrt(sum(v * v for v in values)) or 1.0
        return [v / norm for v in values]

    @staticmethod
    def cosine_similarity(a: list[float], b: list[float]) -> float:
        va = np.array(a)
        vb = np.array(b)
        denom = np.linalg.norm(va) * np.linalg.norm(vb)
        if denom == 0:
            return 0.0
        return float(np.dot(va, vb) / denom)
