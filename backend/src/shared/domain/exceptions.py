"""Domain exceptions for the application."""


class DomainError(Exception):
    """Base exception for domain errors."""


class NotFoundError(DomainError):
    """Exception raised when a requested entity is not found."""


class ForbiddenError(DomainError):
    """Exception raised when an operation is forbidden."""


class ValidationError(DomainError):
    """Exception raised when validation fails."""
