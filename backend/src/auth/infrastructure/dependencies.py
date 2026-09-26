"""Dependency providers for the authentication bounded context infrastructure."""

from src.auth.infrastructure.repositories import SQLAlchemyUserRepository
from src.auth.infrastructure.security.jwt_service import JWTService
from src.shared.infrastructure.dependencies import SessionDep


def get_jwt_service() -> JWTService:
    """Return the JWT service used by the authentication layer."""
    return JWTService()


async def get_user_repository(session: SessionDep) -> SQLAlchemyUserRepository:
    """Return the user repository initialized with the active database session."""
    return SQLAlchemyUserRepository(session)
