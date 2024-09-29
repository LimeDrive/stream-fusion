# Installation de Stremio Trakt Addon avec Docker Compose

Cette documentation vous guidera à travers le processus d'installation de l'addon Stremio Trakt Addon en utilisant Docker Compose.

## Prérequis

Assurez-vous d'avoir rempli tous les [prérequis d'installation](./prerequis.md) avant de commencer.

!!! warning "Important"
    Vérifiez que vous avez bien obtenu toutes les API-Keys nécessaires avant de commencer l'installation.

## Étapes d'installation

### 1. Création du dossier d'installation

Créez un nouveau dossier pour l'installation de l'addon :

```bash
mkdir stremio-trakt-addon
cd stremio-trakt-addon
```

!!! tip "Astuce"
    Choisissez un emplacement facilement accessible pour votre dossier d'installation.

### 2. Création de la base de données

Exécutez la commande suivante pour créer la base de données nécessaire a l'addon :

```bash
docker exec -e PGPASSWORD=stremio stremio-postgres psql -U stremio -d postgres -c "CREATE DATABASE \"stremio-trakt-db\";"
```

!!! note "Note"
    Assurez-vous que le conteneur PostgreSQL de Stremio est en cours d'exécution avant d'exécuter cette commande.

### 3. Création du fichier docker-compose.yml

Créez un fichier `docker-compose.yml` dans le dossier d'installation et copiez-y le contenu suivant :

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

!!! tip "Astuce"
    Vérifiez que le chemin vers le fichier docker-compose.yml est correct dans votre structure de projet.

### 4. Création du fichier .env

Créez un fichier `.env` dans le même dossier et ajoutez-y les variables d'environnement nécessaires :

```env
BASE_URL=https://trakt.example.com
TRAKT_CLIENT_ID=<votre_trakt_client_id>
TRAKT_CLIENT_SECRET=<votre_trakt_client_secret>
```

!!! warning "Attention"
    Ne partagez jamais vos identifiants et secrets client. Gardez-les confidentiels.

### 5. Configuration des variables d'environnement

Voici un tableau détaillant toutes les variables d'environnement disponibles :

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `BASE_URL` | URL de base pour l'addon | (obligatoire) |
| `POSTGRES_USER` | Nom d'utilisateur PostgreSQL | `stremio` |
| `POSTGRES_HOST` | Hôte PostgreSQL | `stremio-postgres` |
| `DB_NAME` | Nom de la base de données | `stremio-trakt-db` |
| `POSTGRES_PASSWORD` | Mot de passe PostgreSQL | `stremio` |
| `POSTGRES_PORT` | Port PostgreSQL | `5432` |
| `DB_MAX_CONNECTIONS` | Nombre maximum de connexions à la DB | `20` |
| `DB_IDLE_TIMEOUT` | Timeout d'inactivité de la DB (ms) | `30000` |
| `DB_CONNECTION_TIMEOUT` | Timeout de connexion à la DB (ms) | `2000` |
| `REDIS_HOST` | Hôte Redis | `stremio-redis` |
| `REDIS_PORT` | Port Redis | `6379` |
| `TRAKT_CLIENT_ID` | ID client Trakt | (obligatoire) |
| `TRAKT_CLIENT_SECRET` | Secret client Trakt | (obligatoire) |
| `TRAKT_HISTORY_FETCH_INTERVAL` | Intervalle de récupération de l'historique Trakt | `1d` |
| `TMDB_CACHE_DURATION` | Durée du cache TMDB | `1d` |
| `TRAKT_CACHE_DURATION` | Durée du cache Trakt | `1d` |
| `LOG_LEVEL` | Niveau de journalisation | `info` |
| `LOG_INTERVAL_DELETION` | Intervalle de suppression des logs | `1d` |
| `NODE_ENV` | Environnement Node.js | `production` |

!!! note "Note"
    Ajustez ces variables selon vos besoins spécifiques. Les valeurs par défaut conviennent à la plupart des configurations.

### 6. Lancement de l'installation

Exécutez la commande suivante pour lancer l'installation :

```bash
docker compose up -d
```

!!! tip "Astuce"
    Utilisez l'option `-d` pour exécuter les conteneurs en arrière-plan.

### 7. Configuration du nom de domaine

Utilisez Nginx Proxy Manager pour relier votre nom de domaine au conteneur `stremio-trakt-addon`. Suivez les étapes de configuration dans Nginx Proxy Manager pour ajouter une nouvelle "Proxy Host" pointant vers le conteneur.

!!! warning "Important"
    Assurez-vous que votre domaine est correctement configuré et que les certificats SSL sont à jour.

## Maintenance

Pour effectuer la maintenance de l'addon, utilisez les commandes Docker Compose suivantes :

* Arrêter l'addon : `docker compose stop`
* Redémarrer l'addon : `docker compose restart`
* Voir les logs : `docker compose logs -f stremio-trakt-addon`
* Mettre à jour l'addon :

  ```bash
  docker compose pull
  docker compose up -d
  ```

!!! tip "Astuce"
    Consultez régulièrement les logs pour vous assurer du bon fonctionnement de l'addon.

## Désinstallation

Pour désinstaller complètement l'addon, suivez ces étapes :

1. Arrêtez et supprimez les conteneurs :
   ```bash
   docker compose down -v
   ```

2. Supprimez la base de données du conteneur PostgreSQL :
   ```bash
   docker exec -e PGPASSWORD=stremio stremio-postgres psql -U stremio -d postgres -c "DROP DATABASE \"stremio-trakt-db\";"
   ```

3. Supprimez le dossier d'installation :
   ```bash
   cd ..
   rm -rf stremio-trakt-addon
   ```

!!! warning "Attention"
    La désinstallation supprimera toutes les données associées a l'addon. Assurez-vous de sauvegarder toutes les informations importantes avant de procéder.

N'oubliez pas de supprimer également la configuration du nom de domaine dans Nginx Proxy Manager si vous ne prévoyez pas de réutiliser ce domaine pour un autre service.

!!! note "Note finale"
    Si vous rencontrez des problèmes lors de l'installation ou de l'utilisation de l'addon, n'hésitez pas à consulter la documentation officielle ou à demander de l'aide sur les forums de support de Stremio ou Trakt.