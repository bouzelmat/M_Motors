"""Authentication routes for register and login."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user, get_db_session
from src.auth.application.commands import (
    RegisterUserCommand,
    RegisterUserCommandHandler,
)
from src.auth.domain.entities import User
from src.auth.domain.value_objects import Email
from src.auth.infrastructure.repositories import SQLAlchemyUserRepository
from src.auth.infrastructure.security.jwt_service import JWTService
from src.auth.infrastructure.security.password_service import PasswordService
from src.shared.domain.exceptions import ValidationError

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


# Pydantic schemas
class RegisterRequest(BaseModel):
    """Request schema for user registration."""

    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)


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
    session: Annotated[AsyncSession, Depends(get_db_session)],
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


@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> LoginResponse:
    """Authenticate user and return access token."""
    user_repository = SQLAlchemyUserRepository(session)
    password_service = PasswordService()
    jwt_service = JWTService()

    # Find user by email
    try:
        email = Email(form_data.username)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        ) from e

    user = await user_repository.find_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Verify password
    if not password_service.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Generate JWT token
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
