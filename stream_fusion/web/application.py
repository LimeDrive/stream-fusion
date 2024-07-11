import os
from importlib import metadata
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, UJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from stream_fusion.constants import NO_CACHE_HEADERS, CustomException
from stream_fusion.logging_config import configure_logging

from stream_fusion.version import get_version
from stream_fusion.web.api.router import api_router
from stream_fusion.web.root.router import root_router
from stream_fusion.web.playback.router import stream_router
from stream_fusion.settings import settings
from stream_fusion.web.lifetime import register_shutdown_event, register_startup_event

APP_ROOT = Path(__file__).parent.parent


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    if not os.environ.get("RUNNING_UNDER_GUNICORN"):
        configure_logging()
    app = FastAPI(
        title="StreamFusion",
        version=str(get_version()),
        docs_url=None,
        redoc_url=None,
        openapi_url="/api/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        content = {
            "success": False, 
            "error": {
                "message": exc.message
            }
        }
    
        return JSONResponse(
            status_code=exc.status_code,
            content=content,
            headers=NO_CACHE_HEADERS
        )
    app.add_middleware(SessionMiddleware, secret_key=settings.session_key)
    # Adds startup and shutdown events.
    register_startup_event(app)
    register_shutdown_event(app)

    # Main router for the API.
    app.include_router(router=root_router)
    app.include_router(router=stream_router)
    app.include_router(router=api_router, prefix="/api")
    # Adds static directory.
    # This directory is used to access swagger files.
    app.mount(
        "/static",
        StaticFiles(directory=APP_ROOT / "static"),
        name="static",
    )

    return app
