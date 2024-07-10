import os
from collections.abc import Awaitable
from typing import Callable
from fastapi import FastAPI
import aiohttp
from stream_fusion.settings import settings


def register_startup_event(
    app: FastAPI,
) -> Callable[[], Awaitable[None]]:
    """
    Actions to run on application startup.
    This function uses fastAPI app to store data
    in the state, such as db_engine and creates a global aiohttp session.
    :param app: the fastAPI application.
    :return: function that actually performs actions.
    """

    @app.on_event("startup")
    async def _startup() -> None:
        app.middleware_stack = None
        app.middleware_stack = app.build_middleware_stack()
        # Initialize aiohttp
        timeout = aiohttp.ClientTimeout(total=settings.aiohttp_timeout)
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=50)
        app.state.http_session = aiohttp.ClientSession(
            timeout=timeout, connector=connector
        )

    return _startup


def register_shutdown_event(
    app: FastAPI,
) -> Callable[[], Awaitable[None]]:
    """
    Actions to run on application's shutdown.
    :param app: fastAPI application.
    :return: function that actually performs actions.
    """

    @app.on_event("shutdown")
    async def _shutdown() -> None:
        if app.state.http_session:
            await app.state.http_session.close()

    return _shutdown
