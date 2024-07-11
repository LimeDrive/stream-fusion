import os

from typing import Any

from gunicorn.app.base import BaseApplication
from gunicorn.util import import_app
from uvicorn.workers import UvicornWorker as BaseUvicornWorker
from stream_fusion.logging_config import configure_logging
from stream_fusion.settings import settings

try:
    import uvloop  # (Found nested import)
except ImportError:
    uvloop = None  # type: ignore  # (variables overlap)


class UvicornWorker(BaseUvicornWorker):
    """
    Configuration for uvicorn workers.

    This class is subclassing UvicornWorker and defines
    some parameters class-wide, because it's impossible,
    to pass these parameters through gunicorn.
    """

    CONFIG_KWARGS = {  # (upper-case constant in a class)  # noqa: RUF012
        "loop": "uvloop" if uvloop is not None else "asyncio",
        "http": "httptools",
        "lifespan": "on",
        "factory": True,
        "proxy_headers": False,
    }


class GunicornApplication(BaseApplication):
    """
    Custom gunicorn application.

    This class is used to start guncicorn
    with custom uvicorn workers.
    """

    def __init__(self, app: str, host: str, port: int, workers: int, timeout: int, **kwargs: Any):
        self.options = {
            "bind": f"{host}:{port}",
            "workers": workers,
            "worker_class": "stream_fusion.gunicorn_runner.UvicornWorker",
            "timeout" : timeout,
            "forwarded_allow_ips" : "*",
            "logconfig_dict": {
                'version': 1,
                'disable_existing_loggers': False,
            },
            **kwargs,
        }
        self.app = app
        super().__init__()

    def load(self) -> str:
        os.environ["RUNNING_UNDER_GUNICORN"] = "1"
        return import_app(self.app)

    def when_ready(self, server):
        configure_logging()

    def load_config(self) -> None:
        """
        Load config for web server.

        This function is used to set parameters to gunicorn
        main process. It only sets parameters that
        gunicorn can handle. If you pass unknown
        parameter to it, it crash with error.
        """
        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None:
                self.cfg.set(key.lower(), value)

    def load(self) -> str:
        """
        Load actual application.

        Gunicorn loads application based on this
        function's returns. We return python's path to
        the app's factory.

        :returns: python path to app factory.
        """
        return import_app(self.app)
