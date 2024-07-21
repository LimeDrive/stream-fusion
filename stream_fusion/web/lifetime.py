import os
from collections.abc import Awaitable
from typing import Callable
from aiohttp_socks import ProxyConnector
from fastapi import FastAPI
import aiohttp
from yarl import URL
from stream_fusion.settings import settings


def register_startup_event(
    app: FastAPI,
) -> Callable[[], Awaitable[None]]:
    @app.on_event("startup")
    async def _startup() -> None:
        app.middleware_stack = None
        app.middleware_stack = app.build_middleware_stack()

        proxy_url = settings.playback_proxy
        if proxy_url:
            parsed_url = URL(proxy_url)
            if parsed_url.scheme in ('socks5', 'socks5h', 'socks4'):
                connector = ProxyConnector.from_url(proxy_url, limit=100, limit_per_host=50)
            elif parsed_url.scheme in ('http', 'https'):
                connector = aiohttp.TCPConnector(limit=100, limit_per_host=50, proxy=proxy_url)
            else:
                raise ValueError(f"Unsupported proxy scheme: {parsed_url.scheme}")
        else:
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=50)

        timeout = aiohttp.ClientTimeout(total=settings.aiohttp_timeout)
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
