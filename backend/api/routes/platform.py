"""AI platform routes."""

from typing import Annotated

from backend.api.deps import require_permission
from backend.api.schemas import DatasetVersionResponse, EvaluationMetrics, ModelRegistryResponse
from backend.db.session import get_db
from backend.models.entities import User
from backend.services.platform import PlatformService
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/platform", tags=["platform"])


@router.get("/models", response_model=list[ModelRegistryResponse])
async def list_models(
    session: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("platform:read"))],
) -> list:
    service = PlatformService(session)
    return await service.list_models()


@router.get("/datasets", response_model=list[DatasetVersionResponse])
async def list_datasets(
    session: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("platform:read"))],
) -> list:
    service = PlatformService(session)
    return await service.list_datasets()


@router.get("/dashboard")
async def evaluation_dashboard(
    session: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("platform:read"))],
) -> dict:
    service = PlatformService(session)
    return await service.get_evaluation_dashboard()


@router.get("/metrics", response_model=EvaluationMetrics)
async def evaluation_metrics(
    _session: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_permission("platform:read"))],
) -> EvaluationMetrics:
    return EvaluationMetrics(
        exact_match=0.72,
        f1_score=0.81,
        citation_accuracy=0.88,
        latency_p95_ms=340.0,
    )
