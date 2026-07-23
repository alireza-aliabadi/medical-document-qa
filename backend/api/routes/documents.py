"""Document upload and management routes."""

from typing import Annotated
from uuid import UUID

from backend.api.deps import require_permission
from backend.api.schemas import DocumentCreateResponse, DocumentResponse
from backend.db.session import get_db
from backend.models.entities import Document, DocumentStatus, User
from backend.services.knowledge_graph import KnowledgeGraphService
from backend.services.storage import StorageService
from backend.workers.tasks import process_document_task
from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentCreateResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: Annotated[UploadFile, File()],
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("documents:write"))],
) -> Document:
    content = await file.read()
    storage = StorageService()
    key = storage.upload_bytes(
        content, file.filename or "document.pdf", file.content_type or "application/pdf"
    )

    document = Document(
        filename=file.filename or "document.pdf",
        content_type=file.content_type or "application/pdf",
        storage_key=key,
        status=DocumentStatus.UPLOADED,
        owner_id=user.id,
    )
    session.add(document)
    await session.flush()
    process_document_task.delay(str(document.id))
    return document


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    session: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("documents:read"))],
) -> list[Document]:
    result = await session.execute(select(Document).order_by(Document.created_at.desc()))
    return list(result.scalars().all())


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("documents:read"))],
) -> Document:
    result = await session.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    if document is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.get("/{document_id}/knowledge-graph")
async def get_document_knowledge_graph(
    document_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("documents:read"))],
) -> dict:
    from backend.models.entities import DocumentChunk

    result = await session.execute(
        select(DocumentChunk).where(DocumentChunk.document_id == document_id).limit(20)
    )
    chunks = list(result.scalars().all())
    text = "\n".join(c.content for c in chunks)
    graph = KnowledgeGraphService().extract(text)
    return graph.to_dict()
