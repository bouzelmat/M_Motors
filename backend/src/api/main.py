"""FastAPI application entrypoint."""

from fastapi import FastAPI

from src.api.rest.health_routes import router as health_router
from src.api.rest.auth_routes import router as auth_router
from src.api.middleware import get_middleware


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(title="M-Motors API", version="0.1.0")
    
    # Include routers
    app.include_router(health_router)
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
    
    # Add middleware
    for middleware in get_middleware():
        app.add_middleware(middleware.cls, **middleware.options)
    
    return app


app = create_app()
