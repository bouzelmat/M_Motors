"""Unit of Work port — domain contract for transactional boundaries.

This module defines the abstract interface (Port) that any Unit of Work
adapter must implement.  Use-cases depend exclusively on this abstraction,
keeping domain and application layers free from any ORM or database details.

Usage in a use-case::

    async with uow:
        repository.add(entity)
        await uow.commit()
"""

from __future__ import annotations

import abc


class AbstractUnitOfWork(abc.ABC):
    """Contract for the Unit of Work pattern.

    A Unit of Work groups one or more repository operations into a single
    atomic transaction.  Concrete adapters (e.g. SQLAlchemy) translate these
    abstract commands into the appropriate database primitives.

    Protocol
    --------
    * Enter the context with ``async with uow:``  — begins the transaction.
    * Call ``await uow.commit()`` to persist all changes permanently.
    * If an exception propagates out of the ``async with`` block **without** an
      explicit commit, ``__aexit__`` automatically triggers ``rollback()``,
      leaving the database in the state it was before the block started.

    Example
    -------
    ::

        async with uow:
            vehicle = Vehicle(...)
            uow.vehicles.add(vehicle)
            await uow.commit()
    """

    # ------------------------------------------------------------------
    # Async context manager protocol
    # ------------------------------------------------------------------

    async def __aenter__(self) -> "AbstractUnitOfWork":
        """Begin a new transactional unit and return this UoW instance."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Rollback automatically when the block exits with an exception.

        If *exc_type* is not ``None`` an error occurred; we roll back any
        partial writes so the database remains in a consistent state.
        If the block completed successfully the caller is expected to have
        already called ``commit()`` explicitly.
        """
        if exc_type is not None:
            await self.rollback()

    # ------------------------------------------------------------------
    # Abstract operations
    # ------------------------------------------------------------------

    @abc.abstractmethod
    async def commit(self) -> None:
        """Persist all pending changes to the database permanently.

        Raises
        ------
        Exception
            Any database or integrity error surfaced by the underlying adapter.
        """

    @abc.abstractmethod
    async def rollback(self) -> None:
        """Discard all pending changes and restore the previous database state.

        This method is called automatically by ``__aexit__`` on failure, but
        can also be invoked explicitly when the use-case logic needs to abort.
        """
