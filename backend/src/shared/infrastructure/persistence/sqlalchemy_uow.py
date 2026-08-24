"""SQLAlchemy Unit of Work adapter.

Translates the abstract ``AbstractUnitOfWork`` port into concrete
SQLAlchemy async-session transaction management.

Typical use inside a use-case
-----------------------------
::

    async with SqlAlchemyUnitOfWork(session_factory) as uow:
        uow.vehicles.add(vehicle)
        await uow.commit()

If any exception escapes the ``async with`` block the session is rolled back
automatically, preventing partial writes from reaching PostgreSQL.
"""

from __future__ import annotations

from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.shared.domain.ports.unit_of_work import AbstractUnitOfWork


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    """Concrete Unit of Work backed by a SQLAlchemy ``AsyncSession``.

    Parameters
    ----------
    session_factory:
        An ``async_sessionmaker`` instance (typically created once at startup
        via :func:`src.shared.infrastructure.database.get_session_factory`).
        A fresh session is created each time this UoW is used as an async
        context manager, so each use-case invocation gets its own isolated
        transactional scope.

    Attributes
    ----------
    session:
        The ``AsyncSession`` that is active for the lifetime of the ``async
        with`` block.  Repository adapters injected into use-cases should
        receive this session so they participate in the same transaction.

    Notes
    -----
    * ``expire_on_commit=False`` is set on the session factory (see
      ``database.py``) so that ORM objects remain accessible after ``commit``
      without triggering an extra SELECT.
    * The ``__aenter__`` / ``__aexit__`` lifecycle is managed by the parent
      class :class:`~src.shared.domain.ports.unit_of_work.AbstractUnitOfWork`;
      this adapter only needs to override ``commit`` and ``rollback``.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
        self.session: AsyncSession  # assigned in __aenter__

    # ------------------------------------------------------------------
    # Async context manager — lifecycle
    # ------------------------------------------------------------------

    async def __aenter__(self) -> Self:
        """Open a new ``AsyncSession`` and begin an implicit transaction."""
        self.session = self._session_factory()
        return await super().__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Delegate to parent (rollback on error) then close the session.

        The session is always closed in the ``finally`` block to guarantee
        that the connection is returned to the pool even when an exception
        occurs during rollback itself.
        """
        try:
            await super().__aexit__(exc_type, exc_val, exc_tb)
        finally:
            await self.session.close()

    # ------------------------------------------------------------------
    # AbstractUnitOfWork implementation
    # ------------------------------------------------------------------

    async def commit(self) -> None:
        """Flush all pending changes and commit the current transaction.

        After a successful commit the session remains open (but clean), so
        the caller can continue using ORM objects returned from repositories
        without hitting an ``DetachedInstanceError``.

        Raises
        ------
        sqlalchemy.exc.SQLAlchemyError
            Propagates any database-level error (constraint violations, dead
            locks, etc.) so the caller can decide how to handle it.
        """
        await self.session.commit()

    async def rollback(self) -> None:
        """Roll back the current transaction, discarding all pending writes.

        This is called automatically by ``__aexit__`` whenever the ``async
        with`` block exits with an unhandled exception.  It can also be
        invoked explicitly inside the block when business logic decides to
        abort an operation mid-way.
        """
        await self.session.rollback()
