from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from logging.config import fileConfig
from sqlalchemy import pool
from users.models import Base

config = context.config
fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_engine():
    return create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        echo=True,
        poolclass=pool.NullPool
    )


async def run_migrations_online():
    """Запуск миграций в асинхронном режиме"""
    connectable = get_engine()

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def do_run_migrations(connection):
    """Прогон миграций"""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    context.configure(url=config.get_main_option("sqlalchemy.url"), target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()
else:
    import asyncio

    asyncio.run(run_migrations_online())
