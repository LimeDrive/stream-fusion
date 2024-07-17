import enum
from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class LogLevel(str, enum.Enum):
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class Settings(BaseSettings):
    """Settings for the application"""

    # STREAM-FUSION
    workers_count: int = 4
    port: int = 8080
    host: str = "0.0.0.0"
    gunicorn_timeout: int = 180
    aiohttp_timeout: int = 3600
    reload: bool = False
    session_key: str = "331cbfe48117fcba53d09572b10d2fc293d86131dc51be46d8aa9843c2e9f48d"
    use_https: bool = False
    # LOGGING
    log_level: LogLevel = LogLevel.INFO
    log_path: str = "/app/config/logs/stream-fusion.log"
    log_redacted: bool = True
    # SECUIRITY
    secret_api_key: str | None = None
    security_hide_docs: bool = True
    # SQLITE
    db_path: str = "/app/config/stream-fusion.db"
    db_echo: bool = False
    db_timeout: int = 15
    # REDIS
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_expiration: int = 604800
    # TMDB
    tmdb_api_key: str | None = None
    # FLARESOLVERR
    flaresolverr_host: str = "localhost"
    flaresolverr_shema: str = "http"
    flaresolverr_port: int = 8191
    # JACKETT
    jackett_host: str = "localhost"
    jackett_shema: str = "http"
    jackett_port: int = 9117
    jackett_api_key: str | None = None
    # ZILEAN DMM API
    zilean_api_key: str | None = None # TODO: check to protéct Zilane API with APIKEY
    zilean_url: str | None = None
    zilean_max_workers: int = 4
    # YGGTORRENT
    ygg_url: str = "https://ygg.re"
    ygg_user: str | None = None
    ygg_pass: str | None = None
    ygg_passkey: str | None = None
    ygg_lime_fix: bool = True
    ygg_proxy_url: str | None = None
    ygg_proxy_apikey: str | None = None
    yggflix_url: str = "https://yggflix.fr"
    yggflix_max_workers: int = 4
    # PUBLIC_CACHE
    public_cache_url: str = "https://stremio-jackett-cacher.elfhosted.com/"
    # DEVELOPMENT
    debug: bool = True
    dev_host: str = "0.0.0.0"
    dev_port: int = 8080
    develop: bool = True
    # VERSION
    version_path: str = "/app/pyproject.toml"

    model_config = SettingsConfigDict(
        env_file=".env", secrets_dir="/run/secrets", env_file_encoding="utf-8"
    )


try:
    settings = Settings()
except ValidationError as e:
    raise RuntimeError(f"Configuration validation error: {e}")
