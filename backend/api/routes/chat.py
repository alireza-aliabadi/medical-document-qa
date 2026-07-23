"""Chat and RAG routes."""

from typing import Annotated
from uuid import UUID

from backend.api.deps import get_current_user, require_permission
from backend.api.schemas import (
    ChatMessageRequest,
    ChatMessageResponse,
    ConversationResponse,
    MessageResponse,
)
from backend.db.session import get_db
from backend.models.entities import Conversation, User
from backend.services.rag import RAGService
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatMessageResponse)
async def chat(
    payload: ChatMessageRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("chat:write"))],
) -> ChatMessageResponse:
    rag = RAGService(session)
    conversation, answer, citations = await rag.chat(
        user_message=payload.message,
        user_id=user.id,
        conversation_id=payload.conversation_id,
        document_ids=payload.document_ids,
    )
    return ChatMessageResponse(
        conversation_id=conversation.id,
        answer=answer,
        citations=citations,
    )


@router.post("/stream")
async def chat_stream(
    payload: ChatMessageRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(require_permission("chat:write"))],
) -> EventSourceResponse:
    rag = RAGService(session)

    async def event_generator():
        async for event in rag.stream_chat(
            user_message=payload.message,
            user_id=user.id,
            conversation_id=payload.conversation_id,
            document_ids=payload.document_ids,
        ):
            yield event

    return EventSourceResponse(event_generator())


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> list[Conversation]:
    result = await session.execute(
        select(Conversation)
        .where(Conversation.user_id == user.id)
        .order_by(Conversation.created_at.desc())
    )
    return list(result.scalars().all())


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    conversation_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("chat:read"))],
) -> list:
    rag = RAGService(session)
    return await rag.get_conversation_history(conversation_id)
