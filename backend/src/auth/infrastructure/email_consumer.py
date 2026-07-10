"""Email consumer for sending welcome emails."""

import logging

from src.auth.domain.events import UserRegistered
from src.shared.infrastructure.event_bus import get_event_bus

logger = logging.getLogger(__name__)


class SendWelcomeEmailOnUserRegistered:
    """Consumer that sends welcome email when user is registered."""

    def __init__(self) -> None:
        """Initialize the email consumer."""
        self._event_bus = get_event_bus()
        # Subscribe to UserRegistered events
        self._event_bus.subscribe(UserRegistered, self.handle)

    async def handle(self, event: UserRegistered) -> None:
        """Handle UserRegistered event by sending welcome email."""
        try:
            # TODO: Implement actual email sending logic
            # For now, we'll just log the event
            logger.info(
                f"Sending welcome email to {event.email} "
                f"for user {event.first_name} {event.last_name}"
            )
            # Placeholder for email service integration
            # await self._email_service.send_welcome_email(
            #     to=event.email,
            #     first_name=event.first_name,
            #     last_name=event.last_name,
            # )
        except Exception as e:
            logger.error(f"Failed to send welcome email to {event.email}: {e}")
            # Don't raise - email failure should not block registration


# Initialize the consumer on module import
_email_consumer = SendWelcomeEmailOnUserRegistered()
