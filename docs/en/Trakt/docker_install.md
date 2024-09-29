# Installing Stremio Trakt Addon with Docker Compose

This documentation will guide you through the process of installing the Stremio Trakt Addon using Docker Compose.

## Prerequisites

Make sure you have fulfilled all the [installation prerequisites](./prerequis.md) before starting.

!!! warning "Important"
    Verify that you have obtained all the necessary API Keys before beginning the installation.

## Installation Steps

### 1. Creating the Installation Folder

Create a new folder for the addon installation:

```bash
mkdir stremio-trakt-addon
cd stremio-trakt-addon
```

!!! tip "Tip"
    Choose an easily accessible location for your installation folder.

### 2. Creating the Database

Execute the following command to create the necessary database for the addon:

```bash
docker exec -e PGPASSWORD=stremio stremio-postgres psql -U stremio -d postgres -c "CREATE DATABASE \"stremio-trakt-db\";"
```

!!! note "Note"
    Ensure that the Stremio PostgreSQL container is running before executing this command.

### 3. Creating the docker-compose.yml File

Create a `docker-compose.yml` file in the installation folder and copy the following content into it:

```yaml
---
networks:
  proxy_network:
    external: true

services:
  stremio-trakt-addon:
    image: reddravenn/stremio-trakt-addon:latest
    container_name: stremio-trakt-addon
    expose:
      - 7000
    restart: unless-stopped
    environment:
      PORT: 7000
      BASE_URL: ${BASE_URL:?Please provide a base URL in the environment}
      DB_USER: ${POSTGRES_USER:-stremio}
      DB_HOST: ${POSTGRES_HOST:-stremio-postgres}
      DB_NAME: ${DB_NAME:-stremio-trakt-db}
      DB_PASSWORD: ${POSTGRES_PASSWORD:-stremio}
      DB_PORT: ${POSTGRES_PORT:-5432}
      DB_MAX_CONNECTIONS: ${DB_MAX_CONNECTIONS:-20}
      DB_IDLE_TIMEOUT: ${DB_IDLE_TIMEOUT:-30000}
      DB_CONNECTION_TIMEOUT: ${DB_CONNECTION_TIMEOUT:-2000}
      REDIS_HOST: ${REDIS_HOST:-stremio-redis}
      REDIS_PORT: ${REDIS_PORT:-6379}
      TRAKT_CLIENT_ID: ${TRAKT_CLIENT_ID:?Please provide a Trakt client ID in the environment}
      TRAKT_CLIENT_SECRET: ${TRAKT_CLIENT_SECRET:?Please provide a Trakt client secret in the environment}
      TRAKT_HISTORY_FETCH_INTERVAL: ${TRAKT_HISTORY_FETCH_INTERVAL:-1d}
      TMDB_CACHE_DURATION: ${TMDB_CACHE_DURATION:-1d}
      TRAKT_CACHE_DURATION: ${TRAKT_CACHE_DURATION:-1d}
      LOG_LEVEL: ${LOG_LEVEL:-info}
      LOG_INTERVAL_DELETION: ${LOG_INTERVAL_DELETION:-1d}
      NODE_ENV: ${NODE_ENV:-production}
    volumes:
      - stremio-trakt-addon-cache:/usr/src/app/cache
      - stremio-trakt-addon-log:/usr/src/app/log
    networks:
      - proxy_network

volumes:
  stremio-trakt-addon-cache:
  stremio-trakt-addon-log:
```

!!! tip "Tip"
    Verify that the path to the docker-compose.yml file is correct in your project structure.

### 4. Creating the .env File

Create a `.env` file in the same folder and add the necessary environment variables:

```env
BASE_URL=https://trakt.example.com
TRAKT_CLIENT_ID=<your_trakt_client_id>
TRAKT_CLIENT_SECRET=<your_trakt_client_secret>
```

!!! warning "Caution"
    Never share your client IDs and secrets. Keep them confidential.

### 5. Configuring Environment Variables

Here's a table detailing all available environment variables:

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `BASE_URL` | Base URL for the addon | (required) |
| `POSTGRES_USER` | PostgreSQL username | `stremio` |
| `POSTGRES_HOST` | PostgreSQL host | `stremio-postgres` |
| `DB_NAME` | Database name | `stremio-trakt-db` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `stremio` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `DB_MAX_CONNECTIONS` | Maximum number of DB connections | `20` |
| `DB_IDLE_TIMEOUT` | DB idle timeout (ms) | `30000` |
| `DB_CONNECTION_TIMEOUT` | DB connection timeout (ms) | `2000` |
| `REDIS_HOST` | Redis host | `stremio-redis` |
| `REDIS_PORT` | Redis port | `6379` |
| `TRAKT_CLIENT_ID` | Trakt client ID | (required) |
| `TRAKT_CLIENT_SECRET` | Trakt client secret | (required) |
| `TRAKT_HISTORY_FETCH_INTERVAL` | Trakt history fetch interval | `1d` |
| `TMDB_CACHE_DURATION` | TMDB cache duration | `1d` |
| `TRAKT_CACHE_DURATION` | Trakt cache duration | `1d` |
| `LOG_LEVEL` | Logging level | `info` |
| `LOG_INTERVAL_DELETION` | Log deletion interval | `1d` |
| `NODE_ENV` | Node.js environment | `production` |

!!! note "Note"
    Adjust these variables according to your specific needs. The default values are suitable for most configurations.

### 6. Launching the Installation

Execute the following command to start the installation:

```bash
docker compose up -d
```

!!! tip "Tip"
    Use the `-d` option to run the containers in the background.

### 7. Configuring the Domain Name

Use Nginx Proxy Manager to link your domain name to the `stremio-trakt-addon` container. Follow the configuration steps in Nginx Proxy Manager to add a new "Proxy Host" pointing to the container.

!!! warning "Important"
    Ensure that your domain is correctly configured and that SSL certificates are up to date.

## Maintenance

To perform addon maintenance, use the following Docker Compose commands:

* Stop the addon: `docker compose stop`
* Restart the addon: `docker compose restart`
* View logs: `docker compose logs -f stremio-trakt-addon`
* Update the addon:

  ```bash
  docker compose pull
  docker compose up -d
  ```

!!! tip "Tip"
    Regularly check the logs to ensure the addon is functioning correctly.

## Uninstallation

To completely uninstall the addon, follow these steps:

1. Stop and remove the containers:
   ```bash
   docker compose down -v
   ```

2. Remove the database from the PostgreSQL container:
   ```bash
   docker exec -e PGPASSWORD=stremio stremio-postgres psql -U stremio -d postgres -c "DROP DATABASE \"stremio-trakt-db\";"
   ```

3. Remove the installation folder:
   ```bash
   cd ..
   rm -rf stremio-trakt-addon
   ```

!!! warning "Caution"
    Uninstallation will remove all data associated with the addon. Make sure to back up any important information before proceeding.

Don't forget to also remove the domain name configuration in Nginx Proxy Manager if you don't plan to reuse this domain for another service.

!!! note "Final Note"
    If you encounter any problems during the installation or use of the addon, don't hesitate to consult the official documentation or ask for help on Stremio or Trakt support forums.