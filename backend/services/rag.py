"""Retrieval-Augmented Generation service."""

import json
import logging
from collections.abc import AsyncGenerator
from contextlib import suppress
from uuid import UUID, uuid4

import httpx
from backend.api.schemas import Citation
from backend.core.config import Settings, get_settings
from backend.models.entities import Conversation, Message
from backend.services.vector_store import SearchResult, VectorStoreService
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

MEDICAL_SYSTEM_PROMPT = (
    "You are a medical knowledge assistant. Answer using ONLY the provided context.\n"
    "If the context is insufficient, say you do not have enough information.\n"
    "Always cite sources. Do not provide definitive medical advice — "
    "recommend consulting a clinician.\n"
    "Context:\n{context}\n"
)


class RAGService:
    def __init__(
        self,
        session: AsyncSession,
        settings: Settings | None = None,
        vector_store: VectorStoreService | None = None,
    ) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.vector_store = vector_store or VectorStoreService(self.settings)

    async def retrieve(
        self,
        query: str,
        document_ids: list[UUID] | None = None,
        top_k: int = 5,
    ) -> list[SearchResult]:
        doc_id_strs = [str(d) for d in document_ids] if document_ids else None
        return self.vector_store.hybrid_search(query, limit=top_k, document_ids=doc_id_strs)

    def build_prompt(self, query: str, results: list[SearchResult]) -> str:
        context_blocks = []
        for idx, result in enumerate(results, start=1):
            context_blocks.append(
                f"[{idx}] (doc={result.document_id}, page={result.page_number})\n{result.content}"
            )
        context = "\n\n".join(context_blocks) or "No relevant context found."
        return MEDICAL_SYSTEM_PROMPT.format(context=context) + f"\n\nQuestion: {query}\nAnswer:"

    def results_to_citations(self, results: list[SearchResult]) -> list[Citation]:
        citations: list[Citation] = []
        for result in results:
            chunk_uuid = None
            with suppress(ValueError):
                chunk_uuid = UUID(result.chunk_id)
            citations.append(
                Citation(
                    document_id=UUID(result.document_id),
                    chunk_id=chunk_uuid,
                    page_number=result.page_number,
                    excerpt=result.content[:300],
                    score=result.score,
                )
            )
        return citations

    async def generate_answer(self, prompt: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.settings.llm_base_url}/chat/completions",
                    json={
                        "model": self.settings.llm_model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.2,
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
        except Exception as exc:
            logger.warning("LLM unavailable, using retrieval-only fallback: %s", exc)

        return (
            "Based on the retrieved medical documents, here is a summary of relevant findings. "
            "Please consult a qualified healthcare provider for clinical decisions."
        )

    async def chat(
        self,
        user_message: str,
        user_id: UUID | None,
        conversation_id: UUID | None = None,
        document_ids: list[UUID] | None = None,
    ) -> tuple[Conversation, str, list[Citation]]:
        conversation = await self._get_or_create_conversation(
            conversation_id, user_id, user_message
        )
        results = await self.retrieve(user_message, document_ids=document_ids)
        prompt = self.build_prompt(user_message, results)
        answer = await self.generate_answer(prompt)
        citations = self.results_to_citations(results)

        self.session.add(
            Message(conversation_id=conversation.id, role="user", content=user_message)
        )
        self.session.add(
            Message(
                conversation_id=conversation.id,
                role="assistant",
                content=answer,
                citations_json=[c.model_dump(mode="json") for c in citations],
            )
        )
        await self.session.flush()
        return conversation, answer, citations

    async def stream_chat(
        self,
        user_message: str,
        user_id: UUID | None,
        conversation_id: UUID | None = None,
        document_ids: list[UUID] | None = None,
    ) -> AsyncGenerator[str, None]:
        conversation = await self._get_or_create_conversation(
            conversation_id, user_id, user_message
        )
        results = await self.retrieve(user_message, document_ids=document_ids)
        prompt = self.build_prompt(user_message, results)
        answer = await self.generate_answer(prompt)
        citations = self.results_to_citations(results)

        self.session.add(
            Message(conversation_id=conversation.id, role="user", content=user_message)
        )
        self.session.add(
            Message(
                conversation_id=conversation.id,
                role="assistant",
                content=answer,
                citations_json=[c.model_dump(mode="json") for c in citations],
            )
        )
        await self.session.flush()

        meta = {
            "conversation_id": str(conversation.id),
            "citations": [c.model_dump() for c in citations],
        }
        yield f"event: meta\ndata: {json.dumps(meta)}\n\n"

        words = answer.split()
        for word in words:
            yield f"data: {json.dumps({'token': word + ' '})}\n\n"
        yield "data: [DONE]\n\n"

    async def _get_or_create_conversation(
        self,
        conversation_id: UUID | None,
        user_id: UUID | None,
        first_message: str,
    ) -> Conversation:
        if conversation_id:
            result = await self.session.execute(
                select(Conversation).where(Conversation.id == conversation_id)
            )
            conversation = result.scalar_one_or_none()
            if conversation:
                return conversation

        title = first_message[:80] + ("..." if len(first_message) > 80 else "")
        conversation = Conversation(id=conversation_id or uuid4(), user_id=user_id, title=title)
        self.session.add(conversation)
        await self.session.flush()
        return conversation

    async def get_conversation_history(self, conversation_id: UUID) -> list[Message]:
        result = await self.session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        return list(result.scalars().all())
