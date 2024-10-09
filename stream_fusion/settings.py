import enum
import multiprocessing
import os
from pydantic import Field, ValidationError, field_validator
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

class DebridService(str, enum.Enum):
    """Possible debrid services."""

    RD = "RD"
    AD = "AD"
    TB = "TB"

def get_default_worker_count():
    """
    Calculate the default number of workers based on CPU cores.
    Returns the number of CPU cores multiplied by 2, with a minimum of 2 and a maximum of 6.
    """
    return min(max(multiprocessing.cpu_count() * 2, 2), 6)

def check_env_variable(var_name):
    value = os.getenv(var_name.upper())
    
    if value and isinstance(value, str) and len(value.strip()) >= 10:
        return True
    return False

class Settings(BaseSettings):
    """Settings for the application"""

    # STREAM-FUSION
    version_path: str = "/app/pyproject.toml"
    workers_count: int = get_default_worker_count()
    port: int = 8080
    host: str = "0.0.0.0"
    gunicorn_timeout: int = 180
    aiohttp_timeout: int = 7200
    session_key: str = Field(
        default_factory=lambda: os.getenv(
            "SESSION_KEY",
            "331cbfe48117fcba53d09572b10d2fc293d86131dc51be46d8aa9843c2e9f48d",
        )
    )
    use_https: bool = False
    download_service: DebridService = DebridService.TB

    # PROXY
    proxied_link: bool = check_env_variable("RD_TOKEN") or check_env_variable("AD_TOKEN")
    proxy_url: str | URL | None = None
    playback_proxy: bool | None = (
        None  # If set, the link will be proxied through the given proxy.
    )

    # REALDEBRID
    rd_token: str | None = None
    rd_unique_account: bool = check_env_variable("RD_TOKEN")
    rd_base_url: str = "https://api.real-debrid.com/rest"
    rd_api_version: str = "1.0"

    # ALLDEBRID
    ad_token: str | None = None
    ad_unique_account: bool = check_env_variable("AD_TOKEN")
    ad_user_app: str = "streamfusion"
    ad_user_ip: str | None = None
    ad_use_proxy: bool = check_env_variable("PROXY_URL")
    ad_base_url: str = "https://api.alldebrid.com"
    ad_api_version: str = "v4"

    # TORBOX
    tb_token: str | None = None
    tb_unique_account: bool = check_env_variable("TB_TOKEN")
    tb_base_url: str = "https://api.torbox.app"
    tb_api_version: str = "v1"

    # LOGGING
    log_level: LogLevel = LogLevel.INFO
    log_path: str = "/app/config/logs/stream-fusion.log"
    log_redacted: bool = True

    # SECUIRITY
    secret_api_key: str | None = None
    security_hide_docs: bool = True

    # POSTGRESQL_DB 
    # TODO: Change the values, but break dev environment
    pg_host: str = "stremio-postgres"
    pg_port: int = 5432
    pg_user: str = "streamfusion" #"stremio"
    pg_pass: str = "streamfusion" #"stremio"
    pg_base: str = "streamfusion"
    pg_echo: bool = False

    # REDIS
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 5
    redis_expiration: int = 604800
    redis_password: str | None = None

    # TMDB
    tmdb_api_key: str | None = None

    # JACKETT
    jackett_host: str = "jackett"
    jackett_schema: str = "http"
    jackett_port: int = 9117
    jackett_api_key: str | None = None
    jackett_enable: bool = check_env_variable("JACKETT_API_KEY")

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
    ygg_unique_account: bool = check_env_variable("YGG_PASSKEY")

    # SHAREWOOD
    sharewood_url: str = "https://www.sharewood.tv"
    sharewood_max_workers: int = 4
    sharewood_passkey: str | None = None
    sharewood_unique_account: bool = check_env_variable("SHAREWOOD_PASSKEY")

    # PUBLIC_CACHE
    public_cache_url: str = "https://stremio-jackett-cacher.elfhosted.com/"

    # DEVELOPMENT
    debug: bool = False
    dev_host: str = "0.0.0.0"
    dev_port: int = 8080
    develop: bool = False
    reload: bool = False

    @field_validator('proxy_url')
    @classmethod
    def validate_and_create_proxy_url(cls, v: str | None) -> URL | None:
        if v is None:
            return None
        
        v = v.strip('"\'')
        if not v.startswith(('http://', 'https://')):
            v = 'http://' + v
        try:
            return URL(v)
        except ValueError as e:
            raise ValueError(f"Invalid proxy URL: {e}")

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
