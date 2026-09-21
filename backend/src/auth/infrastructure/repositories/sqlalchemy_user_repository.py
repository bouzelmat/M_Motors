"""SQLAlchemy implementation of UserRepository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.domain.entities.user import User
from src.auth.domain.ports import UserRepository
from src.auth.domain.value_objects import Email
from src.auth.infrastructure.mappers import UserMapper
from src.auth.infrastructure.orm.user_model import UserModel


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session."""
        self._session = session

    async def save(self, user: User) -> None:
        """Save a user to the database."""
        user_model = UserMapper.to_orm(user)
        self._session.add(user_model)
        await self._session.flush()

    async def find_by_email(self, email: Email) -> User | None:
        """Find a user by email address."""
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == email.value)
        )
        user_model = result.scalar_one_or_none()
        if user_model is None:
            return None
        return UserMapper.to_domain(user_model)

    async def find_by_id(self, id: UUID) -> User | None:
        """Find a user by ID."""
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == str(id))
        )
        user_model = result.scalar_one_or_none()
        if user_model is None:
            return None
        return UserMapper.to_domain(user_model)

    async def email_exists(self, email: Email) -> bool:
        """Check if an email already exists in the repository."""
        result = await self._session.execute(
            select(UserModel.id).where(UserModel.email == email.value)
        )
        return result.scalar_one_or_none() is not None
