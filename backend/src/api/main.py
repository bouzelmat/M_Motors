"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager
import logging
import uuid

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


from src.dossiers.api.routes.admin_dossier_routes import router as admin_dossier_router
from src.auth.api.routes.auth_routes import router as auth_router
from src.dossiers.api.routes.dossier_routes import router as dossier_router
from src.shared.api.routes.health_routes import router as health_router
from src.dossiers.application.consumers.send_dossier_email import (
    SendDocumentsRequestedEmailConsumer,
    SendDossierRejectedEmailConsumer,
    SendDossierValidatedEmailConsumer,
)
from src.dossiers.domain.events.documents_requested import DocumentsRequested
from src.dossiers.domain.events.dossier_rejected import DossierRejected
from src.dossiers.domain.events.dossier_validated import DossierValidated
from src.shared.domain.exceptions import (
    ConflictError,
    DomainError,
    ForbiddenError,
    NotFoundError,
)
from src.shared.infrastructure.messaging.in_memory_event_bus import get_event_bus
from src.shared.infrastructure.http.middleware_registry import get_middleware
from src.vehicles.api.routes.catalog_routes import router as vehicles_router
from src.vehicles.api.routes.photo_routes import router as photos_router

logger = logging.getLogger(__name__)


def _register_event_consumers() -> None:
    """Enregistre les consommateurs d'événements sur le bus singleton."""
    bus = get_event_bus()
    validated_consumer = SendDossierValidatedEmailConsumer()
    bus.subscribe(DossierValidated, validated_consumer.handle)
    rejected_consumer = SendDossierRejectedEmailConsumer()
    bus.subscribe(DossierRejected, rejected_consumer.handle)
    documents_consumer = SendDocumentsRequestedEmailConsumer()
    bus.subscribe(DocumentsRequested, documents_consumer.handle)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gère le démarrage et l'arrêt propre de l'application."""
    _register_event_consumers()
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="M-Motors API",
        version="0.1.0",
        lifespan=lifespan,
        debug=False,  # 🔴 CORRECTION: Désactive le mode debug (Problème 6)
    )

    # --- GLOBAL EXCEPTION HANDLERS ---
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Intercept Pydantic validation errors and return sanitized 422."""
        logger.warning(f"Validation error on {request.url}: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Validation failed",
                "errors": [
                    {
                        "loc": [str(loc) for loc in error["loc"]],
                        "msg": error["msg"],
                        "type": error["type"],
                    }
                    for error in exc.errors()
                ],
            },
        )

    @app.exception_handler(DomainError)
    async def domain_exception_handler(
        request: Request, exc: DomainError
    ) -> JSONResponse:
        """Intercept domain errors and return 422."""
        logger.warning(f"Domain error on {request.method} {request.url}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": "Domain validation failed"},
        )

    @app.exception_handler(NotFoundError)
    async def not_found_exception_handler(
        request: Request, exc: NotFoundError
    ) -> JSONResponse:
        """Intercept NotFoundError and return 404."""
        logger.warning(f"Not found on {request.method} {request.url}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Resource not found"},
        )

    @app.exception_handler(ForbiddenError)
    async def forbidden_exception_handler(
        request: Request, exc: ForbiddenError
    ) -> JSONResponse:
        """Intercept ForbiddenError and return 403."""
        logger.warning(f"Forbidden on {request.method} {request.url}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Access denied"},
        )

    @app.exception_handler(ConflictError)
    async def conflict_exception_handler(
        request: Request, exc: ConflictError
    ) -> JSONResponse:
        """Intercept ConflictError and return 409."""
        logger.warning(f"Conflict on {request.method} {request.url}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Conflict"},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Intercept ALL unhandled exceptions and return sanitized 500."""
        error_id = str(uuid.uuid4())
        logger.exception(
            "Unhandled exception [%s] on %s %s",
            error_id,
            request.method,
            request.url,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error", "error_id": error_id},
        )

    # Include routers
    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(dossier_router)
    app.include_router(admin_dossier_router, prefix="/api/v1")
    app.include_router(vehicles_router)
    app.include_router(photos_router)

    # Add middleware
    for middleware_cls, middleware_options in get_middleware():
        app.add_middleware(middleware_cls, **middleware_options)

    return app


app = create_app()
