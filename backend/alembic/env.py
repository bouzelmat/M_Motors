"""Alembic environment configuration."""

from asyncio import run
from logging.config import fileConfig
import os

from sqlalchemy import pool, create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from src.auth.infrastructure.orm.user_model import Base
from src.shared.infrastructure.config import get_settings

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
target_metadata = Base.metadata

# Set the database URL (Priorité à l'environnement direct pour le staging/migration, sinon les settings)
override_url = os.getenv("DATABASE_URL") or os.getenv("MIGRATION_DATABASE_URL")
if override_url:
    # Si on passe une URL synchrone psycopg, on l'utilise directement.
    db_url = override_url
else:
    settings = get_settings()
    db_url = settings.database_url

config.set_main_option("sqlalchemy.url", db_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with the given connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    # Si l'URL utilise psycopg (synchrone), async_engine_from_config peut lever une erreur si on force l'async.
    # On s'assure d'utiliser le bon moteur selon le driver de l'URL active.
    current_url = config.get_main_option("sqlalchemy.url")

    if "psycopg" in current_url:
        # Mode synchrone direct pour Alembic si on использует psycopg (corrigé sans run_sync)
        connectable = create_engine(current_url, poolclass=pool.NullPool)
        with connectable.connect() as connection:
            do_run_migrations(connection)
        connectable.dispose()
    else:
        # Mode async standard initial (asyncpg)
        connectable = async_engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)

        await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
