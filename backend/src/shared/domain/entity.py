"""Base entity class for domain entities."""

from uuid import UUID
from typing import Any


class Entity:
    """Base class for domain entities with equality based on id."""

    def __init__(self, id: UUID) -> None:
        """Initialize entity with unique identifier."""
        self.id = id

    def __eq__(self, other: Any) -> bool:
        """Check equality based on entity id."""
        if not isinstance(other, Entity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Return hash based on entity id."""
        return hash(self.id)

    def __repr__(self) -> str:
        """Return string representation of entity."""
        return f"{self.__class__.__name__}(id={self.id})"
