"""Mapper between User domain entity and UserModel ORM."""

from uuid import UUID

from src.auth.domain.entities.user import User
from src.auth.domain.value_objects import Email, Role
from src.auth.infrastructure.orm.user_model import UserModel


class UserMapper:
    """Mapper for converting between User entity and UserModel ORM."""

    @staticmethod
    def to_domain(user_model: UserModel) -> User:
        """Convert UserModel ORM to User domain entity."""
        return User(
            id=UUID(str(user_model.id)),
            email=Email(user_model.email),
            hashed_password=user_model.hashed_password,
            first_name=user_model.first_name,
            last_name=user_model.last_name,
            role=Role(user_model.role),
            is_active=user_model.is_active,
            created_at=user_model.created_at,
        )

    @staticmethod
    def to_orm(user: User) -> UserModel:
        """Convert User domain entity to UserModel ORM."""
        return UserModel(
            id=str(user.id),
            email=user.email.value,
            hashed_password=user.hashed_password,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at,
        )
