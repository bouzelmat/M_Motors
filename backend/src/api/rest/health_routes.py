"""HTTP health routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db_session
from src.api.schemas.health_schemas import HealthResponse
from src.shared.infrastructure.database import execute_health_check


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def read_health(
    session: AsyncSession = Depends(get_db_session),
) -> HealthResponse:
    """Validate the database connectivity with a lightweight query."""

    try:
        await execute_health_check(session)
    except Exception as exc:  # pragma: no cover - defensive boundary
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from exc

    return HealthResponse(status="ok", database="reachable")