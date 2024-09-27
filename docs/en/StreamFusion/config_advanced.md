# Advanced Configuration of StreamFusion

This section details all the environment variables that can be configured to customize StreamFusion's behavior. These variables can be passed either as Docker secrets or as container environment variables (in uppercase).

!!! danger "Caution regarding automatic configuration"
    Some environment variables are automatically configured when the application starts, based on your installation. Manually overriding these variables can lead to undesired behavior of StreamFusion, particularly regarding interactions with debridging services.

    The concerned variables include:

    - `PROXIED_LINK`
    - `RD_UNIQUE_ACCOUNT`
    - `AD_UNIQUE_ACCOUNT`
    - `AD_USE_PROXY`
    - `JACKETT_ENABLE`
    - `YGG_UNIQUE_ACCOUNT`
    - `SHAREWOOD_UNIQUE_ACCOUNT`

    Before manually modifying these variables, make sure you understand their impact on the application's functioning. Incorrect configuration could compromise the stability and security of your StreamFusion installation.

## General Variables

| Variable | Description | Default Value |
|----------|-------------|----------------|
| `SESSION_KEY` | Session key for the application | Automatically generated |
| `USE_HTTPS` | Enable HTTPS | `false` |
| `DEFAULT_DEBRID_SERVICE` | Default debridging service | `RD` (RealDebrid) |

!!! info "Session Key"
    The `SESSION_KEY` is automatically generated when the container starts, ensuring a unique key for each StreamFusion installation. This practice enhances the security of your application.

    - It is strongly advised against manually setting this value via an environment variable.
    - The automatic rotation of this key will not affect existing user connections.
    - This approach follows best practices for web application security.

## Server Configuration

| Variable | Description | Default Value |
|----------|-------------|----------------|
| `WORKERS_COUNT` | Number of workers for the application | Automatically calculated |
| `PORT` | Port on which the application listens | `8080` |
| `HOST` | Host on which the application listens | `0.0.0.0` |
| `GUNICORN_TIMEOUT` | Timeout for Gunicorn (in seconds) | `180` |
| `AIOHTTP_TIMEOUT` | Timeout for aiohttp (in seconds) | `7200` |

## Proxy Configuration

| Variable | Description | Default Value |
|----------|-------------|----------------|
| `PROXIED_LINK` | Enable link proxification | Depends on configuration |
| `PROXY_URL` | URL of the proxy to use | `None` |
| `PLAYBACK_PROXY` | Use proxy for stream links from the server | `None` |

!!! info "Functioning of proxy variables"
    - `PROXIED_LINK`: Transforms the application into a proxy, passing all streams through the server. Used to share a debridger account among all users.
    - `PROXY_URL`: Contains the URL of the user's proxy.
    - `PLAYBACK_PROXY`: Applies the proxy to all StreamFusion interactions with debridgers, including streaming links. Useful when `PROXIED_LINK` is enabled, so that video streaming also passes through the configured proxy.

!!! warning "Use of proxies and interactions with debridgers"
    It's important to understand the different aspects of interactions with debridgers:

    1. **Streaming**: Concerns the streaming links of debrided content.
    2. **API Interactions**: Concerns requests to the debridgers' API.

    ---

    - Some debridgers (like AllDebrid) block API requests coming from servers, hence the use of a proxy to contact them.
    - It may happen that server IP addresses are banned by RealDebrid or AllDebrid, preventing even the streaming of video links. In this case, activate `PLAYBACK_PROXY` to pass video playback through the proxy.
    - The use of `PLAYBACK_PROXY` is generally avoided to save resources and reduce latency, except when necessary.

## RealDebrid Configuration

| Variable | Description | Default Value |
|----------|-------------|----------------|
| `RD_TOKEN` | RealDebrid authentication token | `None` |
| `RD_UNIQUE_ACCOUNT` | Use a unique RealDebrid account | Depends on configuration |

## AllDebrid Configuration

| Variable | Description | Default Value |
|----------|-------------|----------------|
| `AD_TOKEN` | AllDebrid authentication token | `None` |
| `AD_UNIQUE_ACCOUNT` | Use a unique AllDebrid account | Depends on configuration |
| `AD_USER_APP` | Application name for AllDebrid | `streamfusion` |
| `AD_USER_IP` | User IP for AllDebrid | `None` |
| `AD_USE_PROXY` | Use a proxy for AllDebrid | Depends on configuration |

## Logging Configuration

| Variable | Description | Default Value |
|----------|-------------|----------------|
| `LOG_LEVEL` | Log level | `INFO` |
| `LOG_PATH` | Path to the log file | `/app/config/logs/stream-fusion.log` |
| `LOG_REDACTED` | Hide sensitive information in logs | `true` |

## Security Configuration

| Variable | Description | Default Value |
|----------|-------------|----------------|
| `SECRET_API_KEY` | Secret API key | `None` |
| `SECURITY_HIDE_DOCS` | Hide API documentation | `true` |

## PostgreSQL Configuration

| Variable | Description | Default Value |
|----------|-------------|----------------|
| `PG_HOST` | PostgreSQL host | `stremio-postgres` |
| `PG_PORT` | PostgreSQL port | `5432` |
| `PG_USER` | PostgreSQL user | `streamfusion` |
| `PG_PASS` | PostgreSQL password | `streamfusion` |
| `PG_BASE` | PostgreSQL database name | `streamfusion` |
| `PG_ECHO` | Enable SQL echo | `false` |

## Redis Configuration

| Variable | Description | Default Value |
|----------|-------------|----------------|
| `REDIS_HOST` | Redis host | `redis` |
| `REDIS_PORT` | Redis port | `6379` |
| `REDIS_DB` | Redis database number | `5` |
| `REDIS_EXPIRATION` | Redis key expiration duration (in seconds) | `604800` |
| `REDIS_PASSWORD` | Redis password | `None` |

## TMDB Configuration

| Variable | Description | Default Value |
|----------|-------------|----------------|
| `TMDB_API_KEY` | TMDB API key | `None` |

## Jackett Configuration

| Variable | Description | Default Value |
|----------|-------------|----------------|
| `JACKETT_HOST` | Jackett host | `jackett` |
| `JACKETT_SCHEMA` | Jackett URL schema | `http` |
| `JACKETT_PORT` | Jackett port | `9117` |
| `JACKETT_API_KEY` | Jackett API key | `None` |
| `JACKETT_ENABLE` | Enable Jackett integration | Depends on configuration |

## Zilean DMM API Configuration

| Variable | Description | Default Value |
|----------|-------------|----------------|
| `ZILEAN_HOST` | Zilean host | `zilean` |
| `ZILEAN_PORT` | Zilean port | `8181` |
| `ZILEAN_SCHEMA` | Zilean URL schema | `http` |
| `ZILEAN_MAX_WORKERS` | Maximum number of Zilean workers | `4` |
| `ZILEAN_POOL_CONNECTIONS` | Zilean connection pool size | `10` |
| `ZILEAN_API_POOL_MAXSIZE` | Zilean API pool maximum size | `10` |
| `ZILEAN_MAX_RETRY` | Maximum number of Zilean retries | `3` |

## YGGFlix Configuration

| Variable | Description | Default Value |
|----------|-------------|----------------|
| `YGGFLIX_URL` | YGGFlix URL | `https://yggflix.fr` |
| `YGGFLIX_MAX_WORKERS` | Maximum number of YGGFlix workers | `4` |
| `YGG_PASSKEY` | YGG passkey | `None` |
| `YGG_UNIQUE_ACCOUNT` | Use a unique YGG account | Depends on configuration |

## Sharewood Configuration

| Variable | Description | Default Value |
|----------|-------------|----------------|
| `SHAREWOOD_URL` | Sharewood URL | `https://www.sharewood.tv` |
| `SHAREWOOD_MAX_WORKERS` | Maximum number of Sharewood workers | `4` |
| `SHAREWOOD_PASSKEY` | Sharewood passkey | `None` |
| `SHAREWOOD_UNIQUE_ACCOUNT` | Use a unique Sharewood account | Depends on configuration |

## Public Cache Configuration

| Variable | Description | Default Value |
|----------|-------------|----------------|
| `PUBLIC_CACHE_URL` | Public cache URL | `https://stremio-jackett-cacher.elfhosted.com/` |

## Development Configuration

| Variable | Description | Default Value |
|----------|-------------|----------------|
| `DEBUG` | Enable debug mode | `false` |
| `DEV_HOST` | Development host | `0.0.0.0` |
| `DEV_PORT` | Development port | `8080` |
| `DEVELOP` | Enable development mode | `false` |
| `RELOAD` | Enable automatic reloading | `false` |

!!! warning "Security"
    Make sure not to expose sensitive information such as tokens and API keys in unsecured environments.