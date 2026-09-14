"""Event Bus port — domain contract for publishing and subscribing to domain events.

This module defines the abstract interface (Port) that any Event Bus adapter
must implement.  Use-cases and domain services depend exclusively on this
abstraction, keeping the domain layer free from any messaging infrastructure.

Usage
-----
::

    # Subscribing a handler (done once at application startup)
    event_bus.subscribe(UserRegistered, send_welcome_email)

    # Publishing an event (done inside a use-case after state change)
    await event_bus.publish(UserRegistered(aggregate_id=user.id))
"""

from __future__ import annotations

import abc
from collections.abc import Awaitable, Callable
from typing import TypeVar

from src.shared.domain.events.domain_event import DomainEvent

# Generic type variable for concrete event sub-types
E = TypeVar("E", bound=DomainEvent)

# Type alias for an async event handler callable
EventHandler = Callable[[DomainEvent], Awaitable[None]]


class AbstractEventBus(abc.ABC):
    """Contract for the Event Bus pattern.

    An Event Bus decouples event producers (use-cases, domain aggregates) from
    event consumers (notification services, projections, side-effect handlers).
    Bounded contexts never import each other directly; instead, they
    communicate exclusively through domain events carried by this bus.

    Protocol
    --------
    * **Subscribe** — register an async callable that will be invoked whenever
      an event of a given type is published:
      ``event_bus.subscribe(EventType, handler_coroutine)``
    * **Publish** — broadcast a domain event to all registered handlers:
      ``await event_bus.publish(event_instance)``

    All handlers must be *async* callables (coroutines) accepting a single
    argument of type :class:`~src.shared.domain.domain_event.DomainEvent`.

    Example
    -------
    ::

        class SendWelcomeEmailHandler:
            async def __call__(self, event: UserRegistered) -> None:
                await email_service.send_welcome(event.user_email)

        event_bus.subscribe(UserRegistered, SendWelcomeEmailHandler())
        await event_bus.publish(UserRegistered(aggregate_id=user.id))
    """

    @abc.abstractmethod
    def subscribe(
        self,
        event_type: type[DomainEvent],
        handler: EventHandler,
    ) -> None:
        """Register *handler* to be called whenever *event_type* is published.

        Parameters
        ----------
        event_type:
            The exact :class:`DomainEvent` subclass to listen for.  Only
            events whose ``type()`` matches *event_type* will be dispatched
            to *handler*.
        handler:
            An async callable ``async def handler(event: DomainEvent) -> None``
            that will be invoked with the published event instance.

        Notes
        -----
        Multiple handlers can be registered for the same *event_type*; they
        will all be called in registration order.
        """

    @abc.abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Broadcast *event* to every handler registered for its type.

        Parameters
        ----------
        event:
            A concrete :class:`DomainEvent` instance to dispatch.

        Notes
        -----
        If no handler is registered for the event type the call is a no-op.
        Implementations must *await* each async handler before moving to the
        next one to preserve a predictable execution order.
        """
