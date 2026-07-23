"""End-to-end document ingestion pipeline."""

import logging
from uuid import UUID

from backend.models.entities import Document, DocumentChunk, DocumentStatus
from backend.services.chunking import ChunkingService
from backend.services.ocr import OCRService
from backend.services.storage import StorageService
from backend.services.vector_store import VectorStoreService
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class DocumentPipelineService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.storage = StorageService()
        self.ocr = OCRService()
        self.chunking = ChunkingService()
        self.vector_store = VectorStoreService()

    async def process_document(self, document_id: UUID) -> None:
        result = await self.session.execute(select(Document).where(Document.id == document_id))
        document = result.scalar_one_or_none()
        if document is None:
            raise ValueError(f"Document {document_id} not found")

        document.status = DocumentStatus.PROCESSING
        await self.session.flush()

        try:
            pdf_bytes = self.storage.download_bytes(document.storage_key)
            extracted = self.ocr.extract(pdf_bytes, document.filename)
            document.page_count = int(extracted.metadata.get("page_count") or 0)
            document.metadata_json = extracted.metadata

            pages = [(p.page_number, p.text) for p in extracted.pages]
            text_chunks = self.chunking.chunk_pages(pages, document_metadata=extracted.metadata)

            db_chunks: list[DocumentChunk] = []
            for tc in text_chunks:
                chunk = DocumentChunk(
                    document_id=document.id,
                    chunk_index=tc.chunk_index,
                    content=tc.content,
                    page_number=tc.page_number,
                    metadata_json=tc.metadata,
                )
                self.session.add(chunk)
                db_chunks.append(chunk)

            await self.session.flush()

            vector_payload = [
                {
                    "chunk_id": chunk.id,
                    "document_id": document.id,
                    "content": chunk.content,
                    "page_number": chunk.page_number,
                    "metadata": chunk.metadata_json or {},
                }
                for chunk in db_chunks
            ]
            vector_ids = self.vector_store.upsert_chunks(vector_payload)
            for chunk, vector_id in zip(db_chunks, vector_ids, strict=True):
                chunk.vector_id = vector_id

            document.status = DocumentStatus.INDEXED
            logger.info("Indexed document %s with %d chunks", document_id, len(db_chunks))
        except Exception as exc:
            document.status = DocumentStatus.FAILED
            document.metadata_json = {**(document.metadata_json or {}), "error": str(exc)}
            logger.exception("Failed to process document %s", document_id)
            raise
