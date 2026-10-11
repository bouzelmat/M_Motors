"""Authentication routes for register and login."""

from typing import Annotated
import re

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field, field_validator

from src.api.dependencies import get_current_user
from src.api.middleware import (
    generate_csrf_token,
    get_client_ip,
    get_login_rate_limit_retry_after,
    record_login_failure,
    record_login_success,
    sign_csrf_token,
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
from src.shared.domain.exceptions import ValidationError

# Remplacement par la dépendance partagée centralisée
from src.shared.infrastructure.dependencies import SessionDep

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


# Pydantic schemas
class RegisterRequest(BaseModel):
    """Request schema for user registration."""

    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, password: str) -> str:
        """Require mixed case, a number, and a special character."""
        requirements = (
            r"[a-z]",
            r"[A-Z]",
            r"\d",
            r"[^A-Za-z0-9]",
        )
        if any(re.search(pattern, password) is None for pattern in requirements):
            raise ValueError(
                "Le mot de passe doit contenir une majuscule, une minuscule, "
                "un chiffre et un caractère spécial."
            )
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
    session: SessionDep,  # Utilisation directe du SessionDep typé et annoté
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
    except ValidationError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e

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
    session: SessionDep,  # Utilisation directe du SessionDep typé et annoté
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
    except ValueError as e:
        record_login_failure(client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        ) from e

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
