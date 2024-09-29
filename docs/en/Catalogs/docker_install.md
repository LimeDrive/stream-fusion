# Installing Stremio Catalog Providers with Docker Compose

This documentation will guide you through the process of installing the Stremio Catalog Providers addon using Docker Compose.

## Prerequisites

Make sure you have met all the [installation prerequisites](./prerequis.md) before starting.

!!! warning "Important"
    Verify that you have obtained all the necessary API Keys before beginning the installation.

## Installation Steps

### 1. Creating the Installation Folder

Create a new folder for the addon installation:

```bash
mkdir stremio-catalog-providers
cd stremio-catalog-providers
```

!!! tip "Tip"
    Choose an easily accessible location for your installation folder.

### 2. Creating the Database

Run the following command to create the database needed for the addon:

```bash
docker exec -e PGPASSWORD=stremio stremio-postgres psql -U stremio -d postgres -c "CREATE DATABASE \"stremio-catalog-db\";"
```

!!! note "Note"
    Make sure the Stremio PostgreSQL container is running before executing this command.

### 3. Creating the docker-compose.yml File

Create a `docker-compose.yml` file in the installation folder and copy the following content:

```yaml
---
networks:
  proxy_network:
    external: true

# Create the DB first : docker exec -e PGPASSWORD=stremio stremio-postgres psql -U stremio -d postgres -c "CREATE DATABASE \"stremio-catalog-db\";"

services:
  stremio-catalog-providers:
    image: reddravenn/stremio-catalog-providers:latest
    container_name: stremio-catalog-providers
    expose:
      - 7000
    restart: unless-stopped
    environment:
      PORT: 7000
      BASE_URL: ${BASE_URL:?Please provide a base URL in the environment}
      DB_USER: ${POSTGRES_USER:-stremio}
      DB_HOST: ${POSTGRES_HOST:-stremio-postgres}
      DB_NAME: ${DB_NAME:-stremio-catalog-db}
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
      CACHE_CATALOG_CONTENT_DURATION_DAYS: ${CACHE_CATALOG_CONTENT_DURATION_DAYS:-1}
      CACHE_POSTER_CONTENT_DURATION_DAYS: ${CACHE_POSTER_CONTENT_DURATION_DAYS:-7}
      LOG_LEVEL: ${LOG_LEVEL:-info}
      LOG_INTERVAL_DELETION: ${LOG_INTERVAL_DELETION:-1d}
      NODE_ENV: ${NODE_ENV:-production}
    volumes:
      - stremio-catalog-logs:/usr/src/app/log
      - stremio-catalog-db:/usr/src/app/db
    networks:
      - proxy_network

volume:
  stremio-catalog-logs:
  stremio-catalog-db:
```

!!! tip "Tip"
    Verify that the path to the catalogs-compose.yml file is correct in your project structure.

### 4. Creating the .env File

Create a `.env` file in the same folder and add the necessary environment variables:

```env
BASE_URL=https://catalogs.example.com
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
| `DB_NAME` | Database name | `stremio-catalog-db` |
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
| `CACHE_CATALOG_CONTENT_DURATION_DAYS` | Catalog cache duration (days) | `1` |
| `CACHE_POSTER_CONTENT_DURATION_DAYS` | Poster cache duration (days) | `7` |
| `LOG_LEVEL` | Logging level | `info` |
| `LOG_INTERVAL_DELETION` | Log deletion interval | `1d` |
| `NODE_ENV` | Node.js environment | `production` |

!!! note "Note"
    Adjust these variables according to your specific needs. The default values are suitable for most configurations.

!!! important "Creating the Trakt.tv Application"
    To obtain the `TRAKT_CLIENT_ID` and `TRAKT_CLIENT_SECRET` credentials, you need to create an application on Trakt.tv. Here's how to proceed:
    
    1. Create an account on [Trakt.tv](https://trakt.tv) if you don't already have one.
    2. Go to the applications section: [https://trakt.tv/oauth/applications](https://trakt.tv/oauth/applications).
    3. Create a new application by filling in the required information (name, description, etc.).
    4. For the redirect URL, use the following format: `BASE_URL + /callback`
       For example, if your `BASE_URL` is `https://catalogs.example.com`, the redirect URL will be `https://catalogs.example.com/callback`.
    5. Once the application is created, you will obtain the `TRAKT_CLIENT_ID` and `TRAKT_CLIENT_SECRET` necessary to configure the addon.

    Remember to keep this information confidential and not share it publicly.

### 6. Launching the Installation

Run the following command to start the installation:

```bash
docker compose up -d
```

!!! tip "Tip"
    Use the `-d` option to run the containers in the background.

### 7. Configuring the Domain Name

Use Nginx Proxy Manager to link your domain name to the `stremio-catalog-providers` container. Follow the configuration steps in Nginx Proxy Manager to add a new "Proxy Host" pointing to the container.

!!! warning "Important"
    Ensure that your domain is correctly configured and that SSL certificates are up to date.

## Maintenance

To perform maintenance on the addon, use the following Docker Compose commands:

* Stop the addon: `docker compose stop`
* Restart the addon: `docker compose restart`
* View logs: `docker compose logs -f stremio-catalog-providers`
* Update the addon:

  ```bash
  docker compose pull
  docker compose up -d
  ```

!!! tip "Tip"
    Regularly check the logs to ensure the addon is functioning properly.

## Uninstallation

To completely uninstall the addon, follow these steps:

1. Stop and remove the containers:
   ```bash
   docker compose down -v
   ```

2. Remove the database from the PostgreSQL container:
   ```bash
   docker exec -e PGPASSWORD=stremio stremio-postgres psql -U stremio -d postgres -c "DROP DATABASE \"stremio-catalog-db\";"
   ```

3. Remove the installation folder:
   ```bash
   cd ..
   rm -rf stremio-catalog-providers
   ```

!!! warning "Caution"
    Uninstallation will remove all data associated with the addon. Make sure to back up any important information before proceeding.

Don't forget to also remove the domain name configuration in Nginx Proxy Manager if you don't plan to reuse this domain for another service.

!!! note "Final Note"
    If you encounter any problems during the installation or use of the addon, don't hesitate to consult the official documentation or ask for help on the support forums.