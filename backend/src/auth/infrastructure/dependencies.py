"""Dependency providers for the authentication bounded context."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.auth.infrastructure.jwt_service import JWTService

from src.auth.domain.entities import User
from src.auth.infrastructure.repositories import SQLAlchemyUserRepository
from src.shared.infrastructure.dependencies import SessionDep

security = HTTPBearer()

CredentialsDep = Annotated[
    HTTPAuthorizationCredentials,
    Depends(security),
]


def get_jwt_service() -> JWTService:
    """Return the JWT service used by the authentication layer."""

    return JWTService()


async def get_user_repository(
    session: SessionDep,
) -> SQLAlchemyUserRepository:
    """Return the user repository."""

    return SQLAlchemyUserRepository(session)


async def get_current_user(
    credentials: CredentialsDep,
    session: SessionDep,
) -> User:
    """Return the currently authenticated user."""

    jwt_service = get_jwt_service()
    user_repository = SQLAlchemyUserRepository(session)

    try:
        payload = jwt_service.decode_token(credentials.credentials)
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from exc

    user = await user_repository.find_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user
