"""Authentication routes for register and login."""

from typing import Annotated
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field, field_validator

from src.auth.api.dependencies import get_current_user
from src.auth.infrastructure.security.csrf import (
    generate_csrf_token,
    sign_csrf_token,
)
from src.auth.infrastructure.security.rate_limiting import (
    get_client_ip,
    get_login_rate_limit_retry_after,
    record_login_failure,
    record_login_success,
)
from src.auth.application.commands import (
    RegisterUserCommand,
    RegisterUserCommandHandler,
)
from src.auth.domain.entities.user import User
from src.auth.domain.value_objects import Email
from src.auth.infrastructure.repositories import SQLAlchemyUserRepository
from src.auth.infrastructure.security.jwt_service import JWTService
from src.auth.infrastructure.security.password_service import PasswordService
from src.shared.domain.exceptions import ConflictError, ValidationError
from src.shared.infrastructure.dependencies import SessionDep

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    """Request schema for user registration."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, password: str) -> str:
        """Validate password without format string risks."""
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.islower() for c in password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isupper() for c in password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in password):
            raise ValueError("Password must contain at least one digit")
        if not any(not c.isalnum() for c in password):
            raise ValueError("Password must contain at least one special character")
        return password


class RegisterResponse(BaseModel):
    """Response schema for user registration."""

    id: str
    email: str
    first_name: str
    last_name: str
    role: str


class LoginResponse(BaseModel):
    """Response schema for user login."""

    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Response schema for user information."""

    id: str
    email: str
    role: str
    first_name: str
    last_name: str
    is_active: bool


@router.post(
    "/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    request: RegisterRequest,
    session: SessionDep,
) -> RegisterResponse:
    """Register a new user account."""
    user_repository = SQLAlchemyUserRepository(session)
    password_service = PasswordService()
    handler = RegisterUserCommandHandler(user_repository, password_service)

    command = RegisterUserCommand(
        email=request.email,
        password=request.password,
        first_name=request.first_name,
        last_name=request.last_name,
    )

    try:
        user = await handler.handle(command)
        await session.commit()
    except ConflictError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        ) from None
    except ValidationError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid registration data",
        ) from None
    # 🔴 CORRECTION: Suppression de `except Exception` (Problème 2)

    return RegisterResponse(
        id=str(user.id),
        email=user.email.value,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role.value,
    )


@router.get("/csrf")
async def get_csrf_token(response: Response) -> dict[str, str]:
    """Issue a CSRF token bound to a cookie for browser-based mutation requests."""
    raw_token = generate_csrf_token()
    signed_token = sign_csrf_token(raw_token)
    response.set_cookie(
        key="csrf_token",
        value=signed_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=3600,
    )
    return {"csrf_token": raw_token}


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
) -> LoginResponse:
    """Authenticate user and return access token."""
    client_ip = get_client_ip(request)
    retry_after = get_login_rate_limit_retry_after(client_ip)
    if retry_after > 0:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts",
            headers={"Retry-After": str(retry_after)},
        )

    user_repository = SQLAlchemyUserRepository(session)
    password_service = PasswordService()
    jwt_service = JWTService()

    try:
        email = Email(form_data.username)
    except ValueError:
        record_login_failure(client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        ) from None

    user = await user_repository.find_by_email(email)
    if user is None:
        record_login_failure(client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not password_service.verify_password(form_data.password, user.hashed_password):
        record_login_failure(client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    record_login_success(client_ip)
    access_token = jwt_service.create_access_token(
        data={"sub": str(user.id), "email": user.email.value}
    )
    return LoginResponse(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    """Get current authenticated user information."""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email.value,
        role=current_user.role.value,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        is_active=current_user.is_active,
    )
