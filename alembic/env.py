import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from app.models.user import Base  # import your Base
from app.core.config import settings

config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata

def get_url():
    return settings.postgresql_url

def run_migrations_online():
    connectable = create_async_engine(get_url(), future=True)

    async def do_run_migrations(connection):
        await connection.run_sync(
            lambda conn: context.configure(
                connection=conn,
                target_metadata=target_metadata,
                compare_type=True,
            )
        )
        await connection.run_sync(context.run_migrations)

    asyncio.run(do_run_migrations(connectable.connect()))

run_migrations_online()
