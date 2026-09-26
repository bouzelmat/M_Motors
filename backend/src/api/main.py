"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.middleware import get_middleware
from src.api.rest.admin_dossier_routes import (
    router as admin_dossier_router,
)
from src.api.rest.auth_routes import router as auth_router
from src.api.rest.dossier_routes import router as dossier_router
from src.api.rest.health_routes import router as health_router
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
