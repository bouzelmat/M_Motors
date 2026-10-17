"""HTTP health routes."""

from fastapi import APIRouter, HTTPException, status

from src.shared.api.schemas.health_schemas import HealthResponse
from src.shared.infrastructure.database import execute_health_check
from src.shared.infrastructure.dependencies import SessionDep

router = APIRouter(tags=["health"])


# ✅ UNE SEULE route, SANS slash final. C'est le standard absolu.
@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def read_health(session: SessionDep) -> HealthResponse:
    """Validate the database connectivity with a lightweight query."""
    try:
        await execute_health_check(session)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from exc
    return HealthResponse(status="ok", database="reachable")
