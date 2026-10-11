"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.api.middleware import get_middleware
from src.api.rest.admin_dossier_routes import (
    router as admin_dossier_router,
)
from src.api.rest.auth_routes import router as auth_router
from src.api.rest.dossier_routes import router as dossier_router
from src.api.rest.health_routes import router as health_router
from src.config import get_settings
from src.dossiers.application.consumers.send_dossier_email import (
    SendDocumentsRequestedEmailConsumer,
    SendDossierRejectedEmailConsumer,
    SendDossierValidatedEmailConsumer,
)
from src.dossiers.domain.events.documents_requested import DocumentsRequested
from src.dossiers.domain.events.dossier_rejected import DossierRejected
from src.dossiers.domain.events.dossier_validated import DossierValidated
from src.shared.infrastructure.messaging.in_memory_event_bus import get_event_bus
from src.vehicles.api.endpoints.catalog import router as vehicles_router
from src.vehicles.api.endpoints.photos import router as photos_router

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
    )

    # --- GLOBAL EXCEPTION HANDLERS ---
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Intercept Pydantic validation errors and return sanitized 422."""
        logger.warning(f"Validation error on {request.url}: {exc.errors()}")
        return JSONResponse(
            status_code=422,
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

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Intercept ALL unhandled exceptions, log them, and return sanitized 500."""
        logger.exception(
            f"Unhandled exception on {request.method} {request.url}: {exc}"
        )
        settings = get_settings()
        if settings.environment == "development":
            # In dev, you might want more details (but NEVER in production)
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "type": type(exc).__name__,
                },
            )
        # In production: NEVER expose stack traces or internal details
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
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
