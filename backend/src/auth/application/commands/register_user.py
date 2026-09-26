"""Register user command and handler."""

from dataclasses import dataclass
from uuid import uuid4

from src.auth.domain.entities.user import User
from src.auth.domain.events import UserRegistered
from src.auth.domain.ports import UserRepository
from src.auth.domain.value_objects import Email, Role
from src.auth.infrastructure.security.password_service import PasswordService
from src.shared.domain.exceptions import ValidationError
from src.shared.infrastructure.event_bus import get_event_bus


@dataclass
class RegisterUserCommand:
    """Command to register a new user."""

    email: str
    password: str
    first_name: str
    last_name: str


class RegisterUserCommandHandler:
    """Handler for RegisterUserCommand."""

    def __init__(
        self,
        user_repository: UserRepository,
        password_service: PasswordService,
    ) -> None:
        """Initialize handler with dependencies."""
        self._user_repository = user_repository
        self._password_service = password_service
        self._event_bus = get_event_bus()

    async def handle(self, command: RegisterUserCommand) -> User:
        """Handle user registration."""
        # Validate email format
        try:
            email = Email(command.email)
        except ValueError as e:
            raise ValidationError(f"Invalid email format: {command.email}") from e

        # Check if email already exists
        if await self._user_repository.email_exists(email):
            raise ValidationError(f"Email already registered: {command.email}")

        # Hash password
        hashed_password = self._password_service.hash_password(command.password)

        # Create user entity
        user = User(
            id=uuid4(),
            email=email,
            hashed_password=hashed_password,
            first_name=command.first_name,
            last_name=command.last_name,
            role=Role.CLIENT,
        )

        # Save user
        await self._user_repository.save(user)

        # Publish domain event
        event = UserRegistered(
            user_id=user.id,
            email=user.email.value,
            first_name=user.first_name,
            last_name=user.last_name,
        )
        await self._event_bus.publish(event)

        return user
