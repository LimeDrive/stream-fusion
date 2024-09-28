# StreamFusion Installation

This page details the process of installing StreamFusion and its dependencies using Docker Compose, offering a simple and efficient method to deploy the entire stack.

## Prerequisites

Before starting the installation, make sure you have fulfilled all the prerequisites mentioned in the [prerequisites page](prerequis.md).

!!! tip "Automatic dependency management"
    Docker Compose will automatically handle the installation of all dependencies, whether mandatory or optional, greatly simplifying the deployment process.

## Installation Steps

Follow these steps to install StreamFusion on your system.

### 1. Creating the Docker network for the proxy

Before configuring the services, we'll create a dedicated Docker network for the proxy. This network will allow secure communication between the different containers in your StreamFusion stack.

Create the Docker network named `proxy_network` with the following command:

```bash
docker network create proxy_network
```

!!! note "Importance of the proxy network"
    Creating a dedicated network for the proxy offers several advantages:

    - Isolation: Services can communicate with each other without being directly exposed to the outside.
    - Security: You can precisely control which containers can communicate with each other.
    - Flexibility: It facilitates adding or removing services without disrupting the rest of the stack.

!!! tip "Network verification"
    You can verify that the network has been correctly created with the command:
    ```bash
    docker network ls
    ```
    You should see `proxy_network` in the list of available networks.

### 2. Creating the directory

Start by creating a new directory dedicated to the StreamFusion stack:

```bash
mkdir streamfusion && cd streamfusion
```

!!! note "Organization"
    This step allows you to keep all StreamFusion-related files in one place, facilitating management and future updates.

### 3. Downloading the docker-compose.yml file

Download the `docker-compose.yml` file from the official GitHub repository:

```bash
curl -O https://raw.githubusercontent.com/LimeDrive/stream-fusion/master/deploy/docker-compose.yml
```

!!! warning "File verification"
    After downloading, it is recommended to check the contents of the file to ensure it hasn't been altered during the transfer.

### 4. Creating the .env file

Create a `.env` file in the same directory to store environment variables:

```bash
nano .env
```

Copy and paste the following content, replacing the values with your own:

```env
# StreamFusion
SECRET_API_KEY='<REDACTED>'
TMDB_API_KEY='<REDACTED>'
JACKETT_API_KEY='<Optional>'
RD_TOKEN='<Optional>'
AD_TOKEN='<Optional>'
YGG_PASSKEY='<Optional>'
SHAREWOOD_PASSKEY='<Optional>'
```

!!! danger "Security of sensitive data"
    Never share your API keys or tokens. Make sure your `.env` file is not publicly accessible and consider using a secrets manager for increased security.

## Configuring environment variables

The following table details each environment variable:

| Variable | Description | Required |
|:----------------|:----------------------------------------------------------------------|:-----------:|
| `SECRET_API_KEY`| Secret key for admin panel access | Yes |
| `TMDB_API_KEY` | API key for The Movie Database | Yes |
| `JACKETT_API_KEY`| API key for Jackett (torrent indexing) | No |
| `RD_TOKEN` | Real-Debrid token for a unique account | No |
| `AD_TOKEN` | AllDebrid token for a unique account | No |
| `YGG_PASSKEY` | YGGTorrent passkey for a unique account | No |
| `SHAREWOOD_PASSKEY`| Sharewood passkey for a unique account | No |

!!! tip "Obtaining API keys"
    To obtain the necessary API keys:
    
    - TMDB: Create an account on [The Movie Database](https://www.themoviedb.org/) and generate an API key in your account settings.
    - Jackett: Install Jackett and find the API key in the web interface.
    - Real-Debrid Token: Here: [Real-Debrid Token](https://real-debrid.com/apitoken).
    - AllDebrid Token: Follow the tutorial here: [AllDebrid Tutorial](../../How-To/apikey_alldebrid.md).

## Launching the Docker Compose stack

Once the `docker-compose.yml` and `.env` files are configured, launch the stack:

```bash
docker compose up -d
```

Verify that all containers are running:

```bash
docker compose ps
```

!!! note "Initialization and configuration"
    - During initialization, Zilean downloads all DMM hashlists and indexes them in the PostgreSQL database.
    - With the current configuration, optimized for low-resource systems, this process can take between 2 and 5 hours, depending on the machine's CPU power.
    - Zilean's IMDB fetching is disabled by default in this configuration to save time and resources.
    - All these options are configurable. For more details, see the [Advanced Configuration](#) section.

!!! tip "Monitoring initialization"
    You can follow the initialization process in real-time with the command:
    ```bash
    docker compose logs -f zilean
    ```

## Updating and management

Keep your StreamFusion installation up-to-date and manage it effectively.

### Updating containers

To update StreamFusion containers:

1. Pull the latest images:
    ```bash
    docker compose pull
    ```

2. Restart the containers with the new images:
    ```bash
    docker compose up -d
    ```

!!! info "Update frequency"
    It is recommended to check for updates at least once a week to benefit from the latest features and security fixes.

### Managing the installation

Useful commands for managing your installation:

- **Stop the stack**: `docker compose down`
- **View logs**: `docker compose logs -f [service_name]`
- **Restart a specific service**: `docker compose restart [service_name]`

!!! tip "Backup"
    Remember to regularly backup your `docker-compose.yml` and `.env` files, as well as Docker volumes if you want to preserve your data. You can automate this process with a backup script.

!!! example "Basic backup script"
    ```bash
    #!/bin/bash
    BACKUP_DIR="/path/to/backups"
    mkdir -p $BACKUP_DIR
    cp docker-compose.yml .env $BACKUP_DIR
    docker compose exec postgres pg_dump -U postgres > $BACKUP_DIR/database_backup.sql
    ```

By following these instructions, you will have a robust and well-managed installation of StreamFusion. Don't hesitate to consult the documentation for more advanced configurations or optimizations specific to your use case.