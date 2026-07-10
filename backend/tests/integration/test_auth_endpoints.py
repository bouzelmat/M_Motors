"""Integration tests for auth endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.rest.auth_routes import router
from src.auth.domain.value_objects import Email
from src.auth.infrastructure.password_service import PasswordService
from src.auth.infrastructure.repositories import SQLAlchemyUserRepository


@pytest.mark.asyncio
async def test_register_user_success(async_client: AsyncClient, db_session: AsyncSession) -> None:
    """Test successful user registration."""
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePass123",
            "first_name": "John",
            "last_name": "Doe",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["role"] == "CLIENT"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_user_duplicate_email(async_client: AsyncClient, db_session: AsyncSession) -> None:
    """Test registration with duplicate email returns 409."""
    # First registration
    await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePass123",
            "first_name": "John",
            "last_name": "Doe",
        },
    )

    # Second registration with same email
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "DifferentPass123",
            "first_name": "Jane",
            "last_name": "Smith",
        },
    )
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_user_invalid_email(async_client: AsyncClient) -> None:
    """Test registration with invalid email format."""
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "invalid-email",
            "password": "SecurePass123",
            "first_name": "John",
            "last_name": "Doe",
        },
    )
    assert response.status_code == 422  # Pydantic validation error


@pytest.mark.asyncio
async def test_register_user_weak_password(async_client: AsyncClient) -> None:
    """Test registration with weak password fails validation."""
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "short",  # Less than 8 characters
            "first_name": "John",
            "last_name": "Doe",
        },
    )
    assert response.status_code == 422  # Pydantic validation error


@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient, db_session: AsyncSession) -> None:
    """Test successful login."""
    # First register a user
    await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePass123",
            "first_name": "John",
            "last_name": "Doe",
        },
    )

    # Then login
    response = await async_client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "SecurePass123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(async_client: AsyncClient, db_session: AsyncSession) -> None:
    """Test login with wrong password returns 401."""
    # First register a user
    await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePass123",
            "first_name": "John",
            "last_name": "Doe",
        },
    )

    # Try login with wrong password
    response = await async_client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "WrongPassword123",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


@pytest.mark.asyncio
async def test_login_nonexistent_user(async_client: AsyncClient) -> None:
    """Test login with non-existent user returns 401."""
    response = await async_client.post(
        "/api/v1/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "SecurePass123",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


@pytest.mark.asyncio
async def test_get_me_without_token(async_client: AsyncClient) -> None:
    """Test accessing /me without token returns 401."""
    response = await async_client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_with_valid_token(async_client: AsyncClient, db_session: AsyncSession) -> None:
    """Test accessing /me with valid token returns user info."""
    # Register and login
    await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePass123",
            "first_name": "John",
            "last_name": "Doe",
        },
    )

    login_response = await async_client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "SecurePass123",
        },
    )
    token = login_response.json()["access_token"]

    # Access /me with token
    response = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["role"] == "CLIENT"
