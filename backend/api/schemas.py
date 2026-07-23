"""Pydantic request/response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentCreateResponse(BaseModel):
    id: UUID
    filename: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    status: str
    page_count: int | None
    metadata_json: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}


class Citation(BaseModel):
    document_id: UUID
    chunk_id: UUID | None = None
    page_number: int | None = None
    excerpt: str
    score: float = 0.0


class ChatMessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    conversation_id: UUID | None = None
    document_ids: list[UUID] | None = None


class ChatMessageResponse(BaseModel):
    conversation_id: UUID
    answer: str
    citations: list[Citation] = Field(default_factory=list)


class ConversationResponse(BaseModel):
    id: UUID
    title: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    citations_json: list | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ModelRegistryResponse(BaseModel):
    id: UUID
    name: str
    version: str
    artifact_uri: str
    metadata_json: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DatasetVersionResponse(BaseModel):
    id: UUID
    name: str
    version: str
    storage_uri: str
    record_count: int
    lineage_json: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}


class EvaluationMetrics(BaseModel):
    exact_match: float
    f1_score: float
    citation_accuracy: float
    latency_p95_ms: float


class AgentToolRequest(BaseModel):
    query: str
    tools: list[str] = Field(default_factory=lambda: ["search", "calculator"])


class AgentToolResponse(BaseModel):
    answer: str
    tool_calls: list[dict]
