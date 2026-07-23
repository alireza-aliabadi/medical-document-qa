"""Qdrant vector store for hybrid retrieval."""

import logging
import uuid
from dataclasses import dataclass

from backend.core.config import Settings, get_settings
from backend.services.embeddings import EmbeddingService
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    chunk_id: str
    document_id: str
    content: str
    score: float
    page_number: int | None
    metadata: dict


class VectorStoreService:
    def __init__(
        self,
        settings: Settings | None = None,
        embedding_service: EmbeddingService | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.embeddings = embedding_service or EmbeddingService(self.settings)
        self.client = QdrantClient(url=self.settings.qdrant_url)
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        collections = [c.name for c in self.client.get_collections().collections]
        if self.settings.qdrant_collection not in collections:
            self.client.create_collection(
                collection_name=self.settings.qdrant_collection,
                vectors_config=qmodels.VectorParams(
                    size=self.settings.embedding_dimension,
                    distance=qmodels.Distance.COSINE,
                ),
            )
            logger.info("Created Qdrant collection %s", self.settings.qdrant_collection)

    def upsert_chunks(
        self,
        chunks: list[dict],
    ) -> list[str]:
        points: list[qmodels.PointStruct] = []
        vector_ids: list[str] = []
        texts = [c["content"] for c in chunks]
        vectors = self.embeddings.embed_texts(texts)

        for chunk, vector in zip(chunks, vectors, strict=True):
            point_id = str(uuid.uuid4())
            vector_ids.append(point_id)
            points.append(
                qmodels.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "chunk_id": str(chunk["chunk_id"]),
                        "document_id": str(chunk["document_id"]),
                        "content": chunk["content"],
                        "page_number": chunk.get("page_number"),
                        "metadata": chunk.get("metadata", {}),
                    },
                )
            )

        self.client.upsert(collection_name=self.settings.qdrant_collection, points=points)
        return vector_ids

    def semantic_search(
        self,
        query: str,
        limit: int = 5,
        document_ids: list[str] | None = None,
    ) -> list[SearchResult]:
        query_vector = self.embeddings.embed_query(query)
        query_filter = None
        if document_ids:
            query_filter = qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="document_id",
                        match=qmodels.MatchAny(any=document_ids),
                    )
                ]
            )

        hits = self.client.search(  # type: ignore[attr-defined]
            collection_name=self.settings.qdrant_collection,
            query_vector=query_vector,
            limit=limit,
            query_filter=query_filter,
        )

        return [
            SearchResult(
                chunk_id=str(hit.payload.get("chunk_id", "")),
                document_id=str(hit.payload.get("document_id", "")),
                content=str(hit.payload.get("content", "")),
                score=float(hit.score or 0.0),
                page_number=hit.payload.get("page_number"),
                metadata=dict(hit.payload.get("metadata") or {}),
            )
            for hit in hits
        ]

    def keyword_search(self, query: str, limit: int = 5) -> list[SearchResult]:
        """Simple keyword fallback using scroll + in-memory filter."""
        tokens = {t.lower() for t in query.split() if len(t) > 2}
        if not tokens:
            return []

        records, _ = self.client.scroll(
            collection_name=self.settings.qdrant_collection,
            limit=256,
            with_payload=True,
            with_vectors=False,
        )
        scored: list[SearchResult] = []
        for record in records:
            payload = record.payload or {}
            content = str(payload.get("content", ""))
            content_lower = content.lower()
            matches = sum(1 for t in tokens if t in content_lower)
            if matches:
                scored.append(
                    SearchResult(
                        chunk_id=str(payload.get("chunk_id", "")),
                        document_id=str(payload.get("document_id", "")),
                        content=content,
                        score=matches / len(tokens),
                        page_number=payload.get("page_number"),
                        metadata=dict(payload.get("metadata") or {}),
                    )
                )
        scored.sort(key=lambda r: r.score, reverse=True)
        return scored[:limit]

    def hybrid_search(
        self,
        query: str,
        limit: int = 5,
        document_ids: list[str] | None = None,
        semantic_weight: float = 0.7,
    ) -> list[SearchResult]:
        semantic = self.semantic_search(query, limit=limit * 2, document_ids=document_ids)
        keyword = self.keyword_search(query, limit=limit * 2)

        combined: dict[str, SearchResult] = {}
        for result in semantic:
            combined[result.chunk_id] = SearchResult(
                chunk_id=result.chunk_id,
                document_id=result.document_id,
                content=result.content,
                score=result.score * semantic_weight,
                page_number=result.page_number,
                metadata=result.metadata,
            )

        kw_weight = 1.0 - semantic_weight
        for result in keyword:
            if result.chunk_id in combined:
                existing = combined[result.chunk_id]
                combined[result.chunk_id] = SearchResult(
                    chunk_id=existing.chunk_id,
                    document_id=existing.document_id,
                    content=existing.content,
                    score=existing.score + result.score * kw_weight,
                    page_number=existing.page_number,
                    metadata=existing.metadata,
                )
            else:
                combined[result.chunk_id] = SearchResult(
                    chunk_id=result.chunk_id,
                    document_id=result.document_id,
                    content=result.content,
                    score=result.score * kw_weight,
                    page_number=result.page_number,
                    metadata=result.metadata,
                )

        ranked = sorted(combined.values(), key=lambda r: r.score, reverse=True)
        return ranked[:limit]
