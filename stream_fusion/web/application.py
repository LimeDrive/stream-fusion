import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import UJSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from stream_fusion.logging_config import configure_logging

from stream_fusion.version import get_version
from stream_fusion.web.api.router import api_router
from stream_fusion.web.root.router import root_router
from stream_fusion.web.playback.router import stream_router
from stream_fusion.settings import settings
from stream_fusion.web.lifespan import lifespan_setup

APP_ROOT = Path(__file__).parent.parent


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """

    configure_logging()
    app = FastAPI(
        title="StreamFusion",
        version=str(get_version()),
        lifespan=lifespan_setup,
        docs_url=None,
        redoc_url=None,
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(SessionMiddleware, secret_key=settings.session_key)

    # Main router for the API.
    app.include_router(router=root_router)
    app.include_router(router=stream_router)
    app.include_router(router=api_router, prefix="/api")
    # Adds static directory.
    # This directory is used to access configs files.
    app.mount(
        "/static",
        StaticFiles(directory=APP_ROOT / "static"),
        name="static",
    )

    return app
