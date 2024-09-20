import aiohttp

from yarl import URL
from fastapi import FastAPI
from redis import ConnectionPool
from typing import AsyncGenerator
from aiohttp_socks import ProxyConnector
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from stream_fusion.logging_config import configure_logging
from stream_fusion.services.postgresql.base import Base
from stream_fusion.services.postgresql.models import load_all_models
from stream_fusion.settings import settings
from stream_fusion.services.postgresql.utils import init_db_cleanup_function


def _setup_db(app: FastAPI) -> None:  # pragma: no cover
    """
    Creates connection to the database.

    This function creates SQLAlchemy engine instance,
    session_factory for creating sessions
    and stores them in the application's state property.

    :param app: fastAPI application.
    """
    engine = create_async_engine(str(settings.pg_url), echo=settings.pg_echo)
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )
    app.state.db_engine = engine
    app.state.db_session_factory = session_factory

    # Need to check if we can add pg_cron to the zileanDB
    # init_db_cleanup_function(engine) 


@asynccontextmanager
async def lifespan_setup(
    app: FastAPI,
) -> AsyncGenerator[None, None]:  # pragma: no cover
    """
    Lifespan context manager for FastAPI application.
    This function handles startup and shutdown events.
    :param app: the FastAPI application.
    :yield: None
    """
    # Startup actions
    app.middleware_stack = None
    _setup_db(app)

    # # Load all models from postgresql/models
    # load_all_models()
    
    # # Create tables
    # async with app.state.db_engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)

    app.middleware_stack = app.build_middleware_stack()

    proxy_url = settings.playback_proxy
    if proxy_url:
        parsed_url = URL(proxy_url)
        if parsed_url.scheme in ("socks5", "socks5h", "socks4"):
            connector = ProxyConnector.from_url(proxy_url, limit=100, limit_per_host=50)
        elif parsed_url.scheme in ("http", "https"):
            connector = aiohttp.TCPConnector(
                limit=100, limit_per_host=50, proxy=proxy_url
            )
        else:
            raise ValueError(f"Unsupported proxy scheme: {parsed_url.scheme}")
    else:
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=50)

    timeout = aiohttp.ClientTimeout(total=settings.aiohttp_timeout)
    app.state.http_session = aiohttp.ClientSession(timeout=timeout, connector=connector)

    app.state.redis_pool = ConnectionPool(
        host=settings.redis_host, port=settings.redis_port, db=0, max_connections=15
    )

    yield

    # Shutdown actions
    if app.state.http_session:
        await app.state.http_session.close()
    if app.state.redis_pool:
        app.state.redis_pool.disconnect()
    await app.state.db_engine.dispose()