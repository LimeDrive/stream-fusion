import uvicorn

from stream_fusion.gunicorn_runner import GunicornApplication
from stream_fusion.logging_config import configure_logging
from stream_fusion.settings import settings


def main() -> None:
    """Entrypoint of the application."""

    configure_logging()
    if settings.reload:
        uvicorn.run(
            "stream_fusion.web.application:get_app",
            workers=settings.workers_count,
            host=settings.host,
            port=settings.port,
            reload=settings.reload,
            reload_excludes=[
                "*.pyc",
                "*.log",
                ".git/*",
                ".vscode/*",
                "tests/*",
                "docs/*",
                ".venv/*",
                ".devcontainer/*",
                ".github/*",
                "Dockerfile",
                "config/*",
            ],
            reload_includes=[
                "*.py",
                "*.html",
                "*.css",
                "*.js",
            ],
            log_level=settings.log_level.value.lower(),
            factory=True,
        )
    else:
        GunicornApplication(
            "stream_fusion.web.application:get_app",
            host=settings.host,
            port=settings.port,
            workers=settings.workers_count,
            timeout=settings.gunicorn_timeout,
            factory=True,
            accesslog="-",
            access_log_format='%r "-" %s "-" %Tf',
            loglevel=settings.log_level.value.lower(),
        ).run()


if __name__ == "__main__":
    main()
