"""Medical AI agent routes."""

from typing import Annotated

from backend.api.deps import require_permission
from backend.api.schemas import AgentToolRequest, AgentToolResponse
from backend.db.session import get_db
from backend.models.entities import User
from backend.services.agent import MedicalAgentService
from backend.services.rag import RAGService
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/run", response_model=AgentToolResponse)
async def run_agent(
    payload: AgentToolRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("chat:write"))],
) -> AgentToolResponse:
    rag = RAGService(session)
    agent = MedicalAgentService(rag)
    answer, tool_calls = await agent.run(payload.query, tools=payload.tools)
    return AgentToolResponse(answer=answer, tool_calls=tool_calls)
