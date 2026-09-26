"""Domain events for auth bounded context."""

from dataclasses import dataclass, field
from uuid import UUID

from src.shared.domain.events.domain_event import DomainEvent


@dataclass(frozen=True)
class UserRegistered(DomainEvent):
    """Event raised when a new user is registered."""

    user_id: UUID = field(default=None)
    email: str = field(default="")
    first_name: str = field(default="")
    last_name: str = field(default="")
