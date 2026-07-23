import asyncio
from uuid import UUID

from backend.db.session import async_session_factory
from backend.services.document_pipeline import DocumentPipelineService
from backend.workers.celery_app import celery_app


async def _process(document_id: UUID) -> None:
    async with async_session_factory() as session:
        pipeline = DocumentPipelineService(session)
        await pipeline.process_document(document_id)
        await session.commit()


@celery_app.task(name="process_document")
def process_document_task(document_id: str) -> str:
    asyncio.run(_process(UUID(document_id)))
    return document_id
