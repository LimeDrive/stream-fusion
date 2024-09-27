# Configuration avancée de StreamFusion

Cette section détaille toutes les variables d'environnement qui peuvent être configurées pour personnaliser le comportement de StreamFusion. Ces variables peuvent être passées soit en tant que secrets Docker, soit en tant que variables d'environnement du conteneur (en majuscules).

!!! danger "Attention à la configuration automatique"
    Certaines variables d'environnement se configurent automatiquement au démarrage de l'application en fonction de votre installation. Surcharger ces variables manuellement peut entraîner des comportements indésirables de StreamFusion, particulièrement en ce qui concerne les interactions avec les services de débridage.

    Les variables concernées incluent notamment :

    - `PROXIED_LINK`
    - `RD_UNIQUE_ACCOUNT`
    - `AD_UNIQUE_ACCOUNT`
    - `AD_USE_PROXY`
    - `JACKETT_ENABLE`
    - `YGG_UNIQUE_ACCOUNT`
    - `SHAREWOOD_UNIQUE_ACCOUNT`

    Avant de modifier manuellement ces variables, assurez-vous de bien comprendre leur impact sur le fonctionnement de l'application. Une configuration incorrecte pourrait compromettre la stabilité et la sécurité de votre installation StreamFusion.

## Variables générales

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `SESSION_KEY` | Clé de session pour l'application | Générée automatiquement |
| `USE_HTTPS` | Activer HTTPS | `false` |
| `DEFAULT_DEBRID_SERVICE` | Service de débridage par défaut | `RD` (RealDebrid) |

!!! info "Session Key"
    La `SESSION_KEY` est générée automatiquement au démarrage du conteneur, garantissant ainsi une clé unique pour chaque installation de StreamFusion. Cette pratique renforce la sécurité de votre application.

    - Il est fortement déconseillé de fixer manuellement cette valeur via une variable d'environnement.
    - La rotation automatique de cette clé n'affectera pas les connexions utilisateurs existantes.
    - Cette approche suit les meilleures pratiques en matière de sécurité pour les applications web.

## Configuration du serveur

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `WORKERS_COUNT` | Nombre de workers pour l'application | Calculé automatiquement |
| `PORT` | Port sur lequel l'application écoute | `8080` |
| `HOST` | Hôte sur lequel l'application écoute | `0.0.0.0` |
| `GUNICORN_TIMEOUT` | Timeout pour Gunicorn (en secondes) | `180` |
| `AIOHTTP_TIMEOUT` | Timeout pour aiohttp (en secondes) | `7200` |

## Configuration du proxy

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `PROXIED_LINK` | Activer la proxification des liens | Dépend de la configuration |
| `PROXY_URL` | URL du proxy à utiliser | `None` |
| `PLAYBACK_PROXY` | Utiliser le proxy pour les lien de stream depuis le serveur | `None` |


!!! info "Fonctionnement des variables de proxy"
    - `PROXIED_LINK` : Transforme l'application en proxy, faisant passer tous les streams par le serveur. Utilisé pour partager un compte de débrideur entre tous les utilisateurs.
    - `PROXY_URL` : Contient l'URL du proxy de l'utilisateur.
    - `PLAYBACK_PROXY` : Applique le proxy à toutes les interactions de StreamFusion avec les débrideurs, y compris les liens de streaming. Utile quand `PROXIED_LINK` est activé, pour que le streaming vidéo passe également par le proxy configuré.

!!! warning "Utilisation des proxys et interactions avec les débrideurs"
    Il est important de comprendre les différents aspects des interactions avec les débrideurs:

    1. **Streaming** : Concerne les liens de streaming des contenus débridés.
    2. **Interactions API** : Concerne les requêtes à l'API des débrideurs.

    ---

    - Certains débrideurs (comme AllDebrid) bloquent les requêtes API provenant de serveurs, d'où l'utilisation d'un proxy pour les contacter.
    - Il peut arriver que des adresses IP de serveurs soient bannies par RealDebrid ou AllDebrid, empêchant même le streaming de liens vidéo. Dans ce cas, activez `PLAYBACK_PROXY` pour faire passer les lectures vidéo par le proxy.
    - L'utilisation de `PLAYBACK_PROXY` est généralement évitée pour économiser les ressources et réduire la latence, sauf en cas de nécessité.

## Configuration de RealDebrid

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `RD_TOKEN` | Token d'authentification RealDebrid | `None` |
| `RD_UNIQUE_ACCOUNT` | Utiliser un compte RealDebrid unique | Dépend de la configuration |

## Configuration d'AllDebrid

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `AD_TOKEN` | Token d'authentification AllDebrid | `None` |
| `AD_UNIQUE_ACCOUNT` | Utiliser un compte AllDebrid unique | Dépend de la configuration |
| `AD_USER_APP` | Nom de l'application pour AllDebrid | `streamfusion` |
| `AD_USER_IP` | IP de l'utilisateur pour AllDebrid | `None` |
| `AD_USE_PROXY` | Utiliser un proxy pour AllDebrid | Dépend de la configuration |

## Configuration Logging

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `LOG_LEVEL` | Niveau de log | `INFO` |
| `LOG_PATH` | Chemin du fichier de log | `/app/config/logs/stream-fusion.log` |
| `LOG_REDACTED` | Masquer les informations sensibles dans les logs | `true` |

## Configuration Sécurité

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `SECRET_API_KEY` | Clé API secrète | `None` |
| `SECURITY_HIDE_DOCS` | Cacher la documentation de l'API | `true` |

## Configuration PostgreSQL

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `PG_HOST` | Hôte PostgreSQL | `stremio-postgres` |
| `PG_PORT` | Port PostgreSQL | `5432` |
| `PG_USER` | Utilisateur PostgreSQL | `streamfusion` |
| `PG_PASS` | Mot de passe PostgreSQL | `streamfusion` |
| `PG_BASE` | Nom de la base de données PostgreSQL | `streamfusion` |
| `PG_ECHO` | Activer l'echo SQL | `false` |

## Configuration Redis

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `REDIS_HOST` | Hôte Redis | `redis` |
| `REDIS_PORT` | Port Redis | `6379` |
| `REDIS_DB` | Numéro de la base de données Redis | `5` |
| `REDIS_EXPIRATION` | Durée d'expiration des clés Redis (en secondes) | `604800` |
| `REDIS_PASSWORD` | Mot de passe Redis | `None` |

## Configuration TMDB

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `TMDB_API_KEY` | Clé API TMDB | `None` |

## Configuration Jackett

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `JACKETT_HOST` | Hôte Jackett | `jackett` |
| `JACKETT_SCHEMA` | Schéma de l'URL Jackett | `http` |
| `JACKETT_PORT` | Port Jackett | `9117` |
| `JACKETT_API_KEY` | Clé API Jackett | `None` |
| `JACKETT_ENABLE` | Activer l'intégration Jackett | Dépend de la configuration |

## Configuration Zilean DMM API

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `ZILEAN_HOST` | Hôte Zilean | `zilean` |
| `ZILEAN_PORT` | Port Zilean | `8181` |
| `ZILEAN_SCHEMA` | Schéma de l'URL Zilean | `http` |
| `ZILEAN_MAX_WORKERS` | Nombre maximum de workers Zilean | `4` |
| `ZILEAN_POOL_CONNECTIONS` | Taille du pool de connexions Zilean | `10` |
| `ZILEAN_API_POOL_MAXSIZE` | Taille maximale du pool API Zilean | `10` |
| `ZILEAN_MAX_RETRY` | Nombre maximum de tentatives Zilean | `3` |

## Configuration YGGFlix

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `YGGFLIX_URL` | URL de YGGFlix | `https://yggflix.fr` |
| `YGGFLIX_MAX_WORKERS` | Nombre maximum de workers YGGFlix | `4` |
| `YGG_PASSKEY` | Passkey YGG | `None` |
| `YGG_UNIQUE_ACCOUNT` | Utiliser un compte YGG unique | Dépend de la configuration |

## Configuration Sharewood

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `SHAREWOOD_URL` | URL de Sharewood | `https://www.sharewood.tv` |
| `SHAREWOOD_MAX_WORKERS` | Nombre maximum de workers Sharewood | `4` |
| `SHAREWOOD_PASSKEY` | Passkey Sharewood | `None` |
| `SHAREWOOD_UNIQUE_ACCOUNT` | Utiliser un compte Sharewood unique | Dépend de la configuration |

## Configuration Cache public

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `PUBLIC_CACHE_URL` | URL du cache public | `https://stremio-jackett-cacher.elfhosted.com/` |

## Configuration de développement

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `DEBUG` | Activer le mode debug | `false` |
| `DEV_HOST` | Hôte de développement | `0.0.0.0` |
| `DEV_PORT` | Port de développement | `8080` |
| `DEVELOP` | Activer le mode développement | `false` |
| `RELOAD` | Activer le rechargement automatique | `false` |

!!! warning "Sécurité"
    Assurez-vous de ne pas exposer les informations sensibles telles que les tokens et les clés API dans des environnements non sécurisés.


