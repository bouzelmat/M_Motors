"""HTTP dependency providers for API routes."""

from typing import Annotated, Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.auth.domain.entities.user import User
from src.auth.domain.value_objects import Role
from src.auth.infrastructure.repositories import SQLAlchemyUserRepository
from src.auth.infrastructure.security.jwt_service import JWTService
from src.shared.infrastructure.dependencies import SessionDep

# HTTPBearer avec auto_error=False pour capturer manuellement l'absence de credentials
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    session: SessionDep,
) -> User:
    """Get current authenticated user from JWT token."""
    if credentials is None or credentials.credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    jwt_service = JWTService()
    user_repository = SQLAlchemyUserRepository(session)

    try:
        payload = jwt_service.decode_token(credentials.credentials)
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from e

    user = await user_repository.find_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


def require_role(required_role: Role) -> Callable[..., User]:
    """Factory dependency enforcing role-based access control (RBAC)."""

    async def role_checker(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        current_role_val = (
            current_user.role.value
            if isinstance(current_user.role, Role)
            else current_user.role
        )
        required_role_val = (
            required_role.value if isinstance(required_role, Role) else required_role
        )

        if current_role_val != required_role_val:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return role_checker


# --- Raccourci pour l'administration ---
require_admin = require_role(Role.ADMIN)
