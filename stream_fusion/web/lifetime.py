import os
from collections.abc import Awaitable
from typing import Callable

from fastapi import FastAPI
import aiohttp

from stream_fusion.settings import settings

global_session: aiohttp.ClientSession = None

def register_startup_event(
    app: FastAPI,
) -> Callable[[], Awaitable[None]]:  # pragma: no cover
    """
    Actions to run on application startup.

    This function uses fastAPI app to store data
    in the state, such as db_engine and creates a global aiohttp session.

    :param app: the fastAPI application.
    :return: function that actually performs actions.
    """

    @app.on_event("startup")
    async def _startup() -> None:
        global global_session
        app.middleware_stack = None
        app.middleware_stack = app.build_middleware_stack()
        
        # TODO: check if globals are better
        # timeout = aiohttp.ClientTimeout(total=settings.aiohttp_timeout)
        # global_session = aiohttp.ClientSession(timeout=timeout)
        # app.state.http_session = global_session

    return _startup


def register_shutdown_event(
    app: FastAPI,
) -> Callable[[], Awaitable[None]]:  # pragma: no cover
    """
    Actions to run on application's shutdown.

    :param app: fastAPI application.
    :return: function that actually performs actions.
    """

    @app.on_event("shutdown")
    async def _shutdown() -> None:
        global global_session
        if global_session:
            await global_session.close()

    return _shutdown