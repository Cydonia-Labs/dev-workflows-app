"""Alembic migration environment configuration.

Configures Alembic to use the application's SQLAlchemy models and
database URL for autogenerating and running migrations.
"""

import os
import sys
from logging.config import fileConfig
from pathlib import Path

# Ensure the backend package is importable when Alembic runs standalone
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy import create_engine

from src.database import Base
from src.models import (  # noqa: F401 — imported for side effects (table registration)
    User,
    Document,
    Section,
    Comment,
    Notification,
    PushSubscription,
    SyncLog,
)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Allow DATABASE_URL env var to override alembic.ini for CI and production
database_url = os.environ.get("DATABASE_URL")
if database_url:
    # Alembic uses synchronous connections; ensure we use psycopg2, not asyncpg
    database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    config.set_main_option("sqlalchemy.url", database_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Generates SQL scripts without connecting to the database.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    Connects to the database and applies migrations directly.
    """
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
