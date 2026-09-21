"""FastAPI application entrypoint."""

from fastapi import FastAPI

from src.api.middleware import get_middleware
from src.api.rest.auth_routes import router as auth_router
from src.api.rest.dossier_routes import router as dossier_router
from src.api.rest.health_routes import router as health_router
from src.vehicles.api.endpoints.catalog import router as vehicles_router
from src.vehicles.api.endpoints.photos import router as photos_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(title="M-Motors API", version="0.1.0")

    # Include routers
    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(dossier_router)
    app.include_router(vehicles_router)
    app.include_router(photos_router)

    # Add middleware
    for middleware_cls, middleware_options in get_middleware():
        app.add_middleware(middleware_cls, **middleware_options)

    return app


app = create_app()
