"""SQLAlchemy Unit of Work adapter.

Translates the abstract ``AbstractUnitOfWork`` port into concrete
SQLAlchemy async-session transaction management.

Typical use inside a use-case
-----------------------------
::

    async with SqlAlchemyUnitOfWork(session) as uow:
        uow.vehicles.add(vehicle)
        await uow.commit()

If any exception escapes the ``async with`` block the session is rolled back
automatically, preventing partial writes from reaching PostgreSQL.
"""

from __future__ import annotations

from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.domain.ports.unit_of_work import AbstractUnitOfWork


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    """Concrete Unit of Work backed by a SQLAlchemy ``AsyncSession``.

    Parameters
    ----------
    session:
        The request-scoped ``AsyncSession`` shared with repositories used by
        the use-case.  Sharing this session is essential: a repository flush
        and the unit of work commit must operate on the same transaction.

    Attributes
    ----------
    session:
        The ``AsyncSession`` that is active for the lifetime of the ``async
        with`` block.  Repository adapters injected into use-cases should
        receive this session so they participate in the same transaction.

    Notes
    -----
    * ``expire_on_commit=False`` keeps ORM objects accessible after ``commit``
      without triggering an extra SELECT.
    * The ``__aenter__`` / ``__aexit__`` lifecycle is managed by the parent
      class :class:`~src.shared.domain.ports.unit_of_work.AbstractUnitOfWork`;
      this adapter only needs to override ``commit`` and ``rollback``.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ------------------------------------------------------------------
    # Async context manager — lifecycle
    # ------------------------------------------------------------------

    async def __aenter__(self) -> Self:
        """Enter the transaction associated with the request session."""
        return await super().__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Rollback on error; FastAPI closes the request session afterwards."""
        await super().__aexit__(exc_type, exc_val, exc_tb)

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
