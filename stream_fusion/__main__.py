import uvicorn

from stream_fusion.gunicorn_runner import GunicornApplication
from stream_fusion.settings import settings


def main() -> None:
    """Entrypoint of the application."""
    if settings.reload:
        uvicorn.run(
            "stream_fusion.web.application:get_app",
            workers=settings.workers_count,
            host=settings.host,
            port=settings.port,
            reload=settings.reload,
            log_level=settings.log_level.value.lower(),
            # TODO: check if factory is needed
            factory=True,
        )
    else:
        # We choose gunicorn only if reload
        # option is not used, because reload
        # feature doen't work with GUvicorn workers.
        GunicornApplication(
            "stream_fusion.web.application:get_app",
            host=settings.host,
            port=settings.port,
            workers=settings.workers_count,
            timeout=settings.gunicorn_timeout,
            factory=True,
            accesslog="-",
            loglevel=settings.log_level.value.lower(),
            access_log_format='%r "-" %s "-" %Tf',
        ).run()


if __name__ == "__main__":
    main()
