# logging_config.py
import os
from loguru import logger
from stream_fusion.settings import settings
import sys
import logging
import inspect
import re
import stackprinter

REDACTED = settings.log_redacted
patterns = [
    r"/ey.*?/",
]

class SecretFilter:
    def __init__(self, patterns):
        self._patterns = patterns

    def __call__(self, record):
        record["message"] = self.redact(record["message"])
        if "stack" in record["extra"]:
            record["extra"]["stack"] = self.redact(record["extra"]["stack"])
        return record

    def redact(self, message):
        for pattern in self._patterns:
            message = re.sub(pattern, "**<REDACTED>**", message)
        return message


def format(record):
    format_ = "{time} {level} {function} {message}\n"
    pats = [
        r"/ey.*?/",
    ]
    if record["exception"] is not None:
        stack = stackprinter.format(
            record["exception"],
            suppressed_vars=[
                r".*ygg_playload.*",
            ],
        )
        if REDACTED:
            for pat in pats:
                stack = re.sub(pat, "/**<REDACTED>**/", stack)
        record["extra"]["stack"] = stack
        format_ += "{extra[stack]}\n"
    return format_

class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

def is_running_under_gunicorn():
    return "gunicorn" in sys.modules

def configure_logging():

    intercept_handler = InterceptHandler()

    logging.basicConfig(handlers=[intercept_handler], level=logging.NOTSET)

    if is_running_under_gunicorn():
        # Configuration spécifique pour Gunicorn
        gunicorn_logger = logging.getLogger('gunicorn.error')
        logger.remove()
        logger.add(gunicorn_logger.handlers[0], format=format, level=gunicorn_logger.level)

    for logger_name in logging.root.manager.loggerDict:
        if logger_name.startswith("uvicorn."):
            logging.getLogger(logger_name).handlers = []

    # change handler for default uvicorn logger
    logging.getLogger("uvicorn").handlers = [intercept_handler]
    logging.getLogger("uvicorn.access").handlers = [intercept_handler]

    logger.remove()

    logger.add(
        sys.stdout,
        format=format,
        level=settings.log_level.value,
        colorize=True,
        filter=SecretFilter(patterns) if REDACTED else None,
    )

    logger.add(
        f"/app/config/logs/api_worker_{os.getpid()}.log",
        format=format,
        level="DEBUG",
        rotation="2 MB",
        retention="5 days",
        compression="zip",
        enqueue=True,
        filter=SecretFilter(patterns) if REDACTED else None,
    )
