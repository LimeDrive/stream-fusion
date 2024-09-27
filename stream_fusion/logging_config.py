import os
import sys
import logging
import inspect
from typing import Union
import stackprinter
import re
from loguru import logger
from stream_fusion.settings import settings

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
            message = re.sub(pattern, "<REDACTED>", message)
        return message

def format_console(record):
    format_ = "<level>{level: <8}</level> | <cyan>{function}</cyan>:<cyan>{line}</cyan> - {message}\n"
    if record["exception"] is not None:
        stack = stackprinter.format(
            record["exception"],
            suppressed_vars=[r".*ygg_playload.*"],
        )
        if REDACTED:
            for pat in patterns:
                stack = re.sub(pat, "/<REDACTED>/", stack)
        record["extra"]["stack"] = stack
        format_ += "\n{extra[stack]}"
    return format_

def format_file(record):
    format_ = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{function}</cyan>:<cyan>{line}</cyan> - {message}\n"
    if record["exception"] is not None:
        stack = stackprinter.format(
            record["exception"],
            suppressed_vars=[r".*ygg_playload.*"],
        )
        if REDACTED:
            for pat in patterns:
                stack = re.sub(pat, "/<REDACTED>/", stack)
        record["extra"]["stack"] = stack
        format_ += "{extra[stack]}\n"
    return format_

class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level: Union[str, int] = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

def configure_logging() -> None:
    logger.remove()  # Remove default handler

    log_level = settings.log_level.value

    logger.add(
        sys.stdout,
        format=format_console,
        level=log_level,
        colorize=True,
        backtrace=True,
        diagnose=True,
        filter=SecretFilter(patterns) if REDACTED else None,
        enqueue=True
    )

    # File logging
    logger.add(
        f"/app/config/logs/api_worker_{os.getpid()}.log",
        format=format_file,
        level="DEBUG",
        rotation="2 MB",
        retention="5 days",
        compression="zip",
        enqueue=True,
        filter=SecretFilter(patterns) if REDACTED else None,
    )

    # Intercept standard library logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Disable uvicorn access logs
    for logger_name in logging.root.manager.loggerDict:
        if logger_name.startswith("uvicorn."):
            logging.getLogger(logger_name).handlers = []

    # Explicitly handle uvicorn loggers
    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logging.getLogger(logger_name).handlers = [InterceptHandler()]