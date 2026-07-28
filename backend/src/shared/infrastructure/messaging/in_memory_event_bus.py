"""In-memory Event Bus adapter.

Implements :class:`~src.shared.domain.ports.event_bus.AbstractEventBus` using
a plain Python dictionary stored in RAM.  Events are dispatched *synchronously*
within the same process, awaiting each registered handler in sequence before
returning control to the caller.

This adapter is the default implementation for all environments (development,
test, production single-process).  It can be swapped for a distributed message
broker (RabbitMQ, Kafka, etc.) by providing an alternative adapter that
respects the same ``AbstractEventBus`` interface.

Typical setup at application startup
-------------------------------------
::

    from src.shared.infrastructure.messaging.in_memory_event_bus import (
        InMemoryEventBus,
        get_event_bus,
    )
    from src.auth.application.event_handlers import send_welcome_email

    bus = get_event_bus()
    bus.subscribe(UserRegistered, send_welcome_email)
"""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from collections.abc import Awaitable, Callable

from src.shared.domain.domain_event import DomainEvent
from src.shared.domain.ports.event_bus import AbstractEventBus, EventHandler

logger = logging.getLogger(__name__)


class InMemoryEventBus(AbstractEventBus):
    """Concrete Event Bus that stores handlers in an in-process dictionary.

    Handlers are grouped by their target event type in ``_handlers``.  When
    ``publish`` is called, the bus looks up the event's concrete type and
    awaits each registered handler in registration order.

    Thread / concurrency safety
    ---------------------------
    This implementation is safe for use within a single ``asyncio`` event
    loop.  It does **not** add thread-locking because FastAPI / Starlette
    applications run in a single event loop.  If you ever need to dispatch
    events from multiple threads, wrap calls in ``loop.call_soon_threadsafe``.

    Error isolation
    ---------------
    If a handler raises an exception it is caught, logged at ``ERROR`` level,
    and the remaining handlers for the same event are still executed.  This
    prevents a misbehaving subscriber from silently swallowing all subsequent
    side-effects.
    """

    def __init__(self) -> None:
        # defaultdict avoids a conditional check on every subscribe call
        self._handlers: dict[type[DomainEvent], list[EventHandler]] = defaultdict(list)

    # ------------------------------------------------------------------
    # AbstractEventBus implementation
    # ------------------------------------------------------------------

    def subscribe(
        self,
        event_type: type[DomainEvent],
        handler: EventHandler,
    ) -> None:
        """Register *handler* for *event_type*.

        Parameters
        ----------
        event_type:
            The :class:`DomainEvent` subclass to listen for.
        handler:
            An async callable invoked with the published event instance.
        """
        self._handlers[event_type].append(handler)
        logger.debug(
            "EventBus: subscribed '%s' to '%s'",
            getattr(handler, "__name__", repr(handler)),
            event_type.__name__,
        )

    async def publish(self, event: DomainEvent) -> None:
        """Dispatch *event* to all handlers registered for its concrete type.

        Each handler is awaited sequentially.  Exceptions raised by individual
        handlers are caught and logged so that subsequent handlers are not
        skipped.

        Parameters
        ----------
        event:
            A concrete :class:`DomainEvent` instance to broadcast.
        """
        event_type = type(event)
        handlers = self._handlers.get(event_type, [])

        if not handlers:
            logger.debug(
                "EventBus: no handlers registered for '%s', skipping.",
                event_type.__name__,
            )
            return

        logger.debug(
            "EventBus: publishing '%s' (id=%s) to %d handler(s).",
            event_type.__name__,
            event.event_id,
            len(handlers),
        )

        for handler in handlers:
            try:
                await handler(event)
            except Exception:  # noqa: BLE001
                logger.exception(
                    "EventBus: handler '%s' raised an exception while "
                    "processing '%s' (id=%s). Continuing with next handler.",
                    getattr(handler, "__name__", repr(handler)),
                    event_type.__name__,
                    event.event_id,
                )

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def clear_handlers(self, event_type: type[DomainEvent] | None = None) -> None:
        """Remove registered handlers — useful in unit tests.

        Parameters
        ----------
        event_type:
            If provided, only the handlers for that specific event type are
            cleared.  If ``None``, **all** handlers are removed.
        """
        if event_type is None:
            self._handlers.clear()
        else:
            self._handlers.pop(event_type, None)

    @property
    def handler_count(self) -> int:
        """Total number of handlers registered across all event types."""
        return sum(len(h) for h in self._handlers.values())


# ---------------------------------------------------------------------------
# Application-level singleton
# ---------------------------------------------------------------------------

_event_bus: InMemoryEventBus | None = None


def get_event_bus() -> InMemoryEventBus:
    """Return the application-wide singleton ``InMemoryEventBus`` instance.

    The instance is created lazily on first call and reused for the lifetime
    of the process.  All subscriptions made at startup are therefore preserved
    across every request handled by the application.

    Returns
    -------
    InMemoryEventBus
        The shared bus instance.
    """
    global _event_bus  # noqa: PLW0603
    if _event_bus is None:
        _event_bus = InMemoryEventBus()
        logger.info("EventBus: InMemoryEventBus singleton created.")
    return _event_bus
