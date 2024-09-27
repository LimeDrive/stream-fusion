from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine

from stream_fusion.logging_config import logger
from stream_fusion.settings import settings


async def create_database() -> None:
    """Create a database."""
    db_url = make_url(str(settings.pg_url.with_path("/postgres")))
    engine = create_async_engine(db_url, isolation_level="AUTOCOMMIT")

    async with engine.connect() as conn:
        database_existance = await conn.execute(
            text(
                f"SELECT 1 FROM pg_database WHERE datname='{settings.pg_base}'",  # noqa: S608
            ),
        )
        database_exists = database_existance.scalar() == 1

    if database_exists:
        await drop_database()

    async with engine.connect() as conn:
        await conn.execute(
            text(
                f'CREATE DATABASE "{settings.pg_base}" ENCODING "utf8" TEMPLATE template1',  # noqa: E501
            ),
        )


async def drop_database() -> None:
    """Drop current database."""
    db_url = make_url(str(settings.pg_url.with_path("/postgres")))
    engine = create_async_engine(db_url, isolation_level="AUTOCOMMIT")
    async with engine.connect() as conn:
        disc_users = (
            "SELECT pg_terminate_backend(pg_stat_activity.pid) "  # noqa: S608
            "FROM pg_stat_activity "
            f"WHERE pg_stat_activity.datname = '{settings.pg_base}' "
            "AND pid <> pg_backend_pid();"
        )
        await conn.execute(text(disc_users))
        await conn.execute(text(f'DROP DATABASE "{settings.pg_base}"'))


async def init_db_cleanup_function(engine):
    async with engine.begin() as conn:
        result = await conn.execute(text(
            "SELECT 1 FROM pg_proc WHERE proname = 'delete_expired_api_keys'"
        ))
        function_exists = result.scalar() is not None

        if not function_exists:
            await conn.execute(text("""
            CREATE OR REPLACE FUNCTION delete_expired_api_keys() RETURNS void AS $$
            BEGIN
                DELETE FROM api_keys
                WHERE NOT never_expire
                  AND expiration_date < NOW() - INTERVAL '7 days'
                  AND (latest_query_date IS NULL OR latest_query_date < NOW() - INTERVAL '7 days');
                RAISE NOTICE 'Deleted % expired API keys', ROW_COUNT;
            END;
            $$ LANGUAGE plpgsql;
            """))

            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_cron;"))

            await conn.execute(text("""
            SELECT cron.schedule('0 */6 * * *', $$SELECT delete_expired_api_keys()$$);
            """))

            logger.info("API key cleanup function created and scheduled.")
        else:
            logger.info("API key cleanup function already exists.")