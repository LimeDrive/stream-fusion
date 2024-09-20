import enum
import multiprocessing
import os
from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict
from yarl import URL


class LogLevel(str, enum.Enum):
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"

def get_default_worker_count():
    """
    Calculate the default number of workers based on CPU cores.
    Returns the number of CPU cores multiplied by 2, with a minimum of 2 and a maximum of 6.
    """
    return min(max(multiprocessing.cpu_count() * 2, 2), 6)

class Settings(BaseSettings):
    """Settings for the application"""

    # STREAM-FUSION
    version_path: str = "/app/pyproject.toml"
    workers_count: int = Field(default_factory=get_default_worker_count)
    port: int = 8080
    host: str = "0.0.0.0"
    gunicorn_timeout: int = 180
    aiohttp_timeout: int = 7200
    proxied_link: bool = (
        True  # TODO: Doccu that is set to True to use the proxy by default, to advoid WARN from Realdebrid
    )
    playback_proxy: str | None = (
        None  # If set, the link will be proxied through the given proxy.
    )
    session_key: str = Field(
        default_factory=lambda: os.getenv(
            "SESSION_KEY",
            "331cbfe48117fcba53d09572b10d2fc293d86131dc51be46d8aa9843c2e9f48d",
        )
    )
    use_https: bool = False

    # LOGGING
    log_level: LogLevel = LogLevel.INFO
    log_path: str = "/app/config/logs/stream-fusion.log"
    log_redacted: bool = True

    # SECUIRITY
    secret_api_key: str | None = None
    security_hide_docs: bool = True


    # POSTGRESQL_DB
    pg_host: str = "postgresql"
    pg_port: int = 5432
    pg_user: str = "streamfusion"
    pg_pass: str = "streamfusion"
    pg_base: str = "streamfusion"
    pg_echo: bool = False

    # REDIS
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_expiration: int = 604800
    redis_password: str | None = None

    # TMDB
    tmdb_api_key: str | None = None

    # JACKETT
    jackett_host: str = "jackett"
    jackett_schema: str = "http"
    jackett_port: int = 9117
    jackett_api_key: str | None = None

    # ZILEAN DMM API
    zilean_host: str = "zilean"
    zilean_port: int = 8181
    zilean_schema: str = "http"
    zilean_max_workers: int = 4
    zilean_pool_connections: int = 10
    zilean_api_pool_maxsize: int = 10
    zilean_max_retry: int = 3

    # YGGFLIX
    yggflix_url: str = "https://yggflix.fr"
    yggflix_max_workers: int = 4
    ygg_passkey: str | None = None

    # SHAREWOOD
    sharewood_url: str = "https://www.sharewood.tv"
    sharewood_max_workers: int = 4
    sharewood_passkey: str | None = None

    # PUBLIC_CACHE
    public_cache_url: str = "https://stremio-jackett-cacher.elfhosted.com/"

    # DEVELOPMENT
    debug: bool = True
    dev_host: str = "0.0.0.0"
    dev_port: int = 8080
    develop: bool = True
    reload: bool = False

    @property
    def pg_url(self) -> URL:
        """
        Assemble database URL from settings.

        :return: database URL.
        """
        return URL.build(
            scheme="postgresql+asyncpg",
            host=self.pg_host,
            port=self.pg_port,
            user=self.pg_user,
            password=self.pg_pass,
            path=f"/{self.pg_base}",
        )
    @property
    def jackett_url(self) -> URL:
        """
        Assemble Jackett URL from settings.
        :return: Jackett URL.
        """
        url = URL.build(
            scheme=self.jackett_schema,
            host=self.jackett_host,
            port=self.jackett_port,
        )
        if self.jackett_api_key:
            url = url.with_query({"apikey": self.jackett_api_key})
        return url

    @property
    def zilean_url(self) -> URL:
        """
        Assemble Zilean URL from settings.
        :return: Zilean URL.
        """
        return URL.build(
            scheme=self.zilean_schema,
            host=self.zilean_host,
            port=self.zilean_port,
        )

    @property
    def redis_url(self) -> URL:
        """
        Assemble Redis URL from settings.
        :return: Redis URL.
        """
        url = URL.build(
            scheme="redis",
            host=self.redis_host,
            port=self.redis_port,
        )
        if self.redis_password:
            url = url.with_password(self.redis_password)
        return url

    model_config = SettingsConfigDict(
        env_file=".env", secrets_dir="/run/secrets", env_file_encoding="utf-8"
    )


try:
    settings = Settings()
except ValidationError as e:
    raise RuntimeError(f"Configuration validation error: {e}")
