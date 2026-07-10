"""HTTP dependency providers."""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.infrastructure.database import get_session
from src.auth.domain.entities import User
from src.auth.domain.ports import UserRepository
from src.auth.infrastructure.jwt_service import JWTService
from src.auth.infrastructure.repositories import SQLAlchemyUserRepository

security = HTTPBearer()


async def get_db_session() -> AsyncIterator[AsyncSession]:
	"""Yield the request-scoped database session used by HTTP routes."""

	async for session in get_session():
		yield session


async def get_current_user(
	credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
	session: Annotated[AsyncSession, Depends(get_db_session)],
) -> User:
	"""Get current authenticated user from JWT token."""
	jwt_service = JWTService()
	user_repository = SQLAlchemyUserRepository(session)

	try:
		payload = jwt_service.decode_token(credentials.credentials)
		user_id: str = payload.get("sub")
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
