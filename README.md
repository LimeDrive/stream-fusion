<h1 align="center">StreamFusion</h1>
<p align="center" style="font-size: 1.5em; font-weight: bold;">Optimisé pour le contenu francophone</p>

<p align="center">
  <img src="stream_fusion/static/logo-stream-fusion.png" alt="StreamFusion Logo"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/licence-MIT-blue.svg" alt="Licence MIT">
  <img src="https://img.shields.io/github/v/release/limedrive/stream-fusion?include_prereleases" alt="Version">
  <img src="https://img.shields.io/github/issues/limedrive/stream-fusion" alt="Problèmes ouverts">
  <img src="https://img.shields.io/github/issues-pr/limedrive/stream-fusion" alt="Pull Requests">
  <img src="https://img.shields.io/github/last-commit/limedrive/stream-fusion" alt="Dernière mise à jour">
</p>


## Description

StreamFusion est un addon avancé pour Stremio qui améliore considérablement ses capacités de streaming, spécialement optimisé pour le contenu francophone. Il intègre des indexeurs de torrents via jackett, des services de debrid et des fonctionnalités avancées pour offrir une expérience de streaming fluide et complète, particulièrement adaptée au public français.

## Caractéristiques principales

- **Intégration d'indexeurs français** : Utilise les principaux indexeurs français, soit en direct soit via Jackett.
- **Catalogue YggFlix** : Ajout du catalogue YggFlix directement dans Stremio.
- **Cache public de Stremio-Jackett** : Utilisation du cache du projet d'origine pour des performances optimales.
- **Intégration de Zilean** : Indexation de toutes les hashlist de DébridMediaManager pour accéder aux contenus en cache chez les débrideurs.
- **FlareSolverr** : Intégration directe pour de meilleures performances face aux protections Cloudflare (actuellement en stand-by).
- **Intégration de Real-Debrid** : Redistribution des liens de streaming en direct, ajout de torrents depuis Stremio (d'autres débrideurs seront ajoutés à l'avenir).
- **Proxification des flux** : Option pour proxifier les flux vidéo.
- **Sécurité renforcée** : Protection de l'application avec clé API via une interface de gestion.
- **Tri optimisé pour le contenu français** : Résultats ciblés et de qualité, avec reconnaissance des langues et des teams.
- **Gestion du cache avec Redis** : Amélioration des performances et de la rapidité des résultats.
- **Déploiement Docker** : Possibilité de déploiement en self-hosted via Docker et docker-compose.

## Mises à jour à venir

- Ajout de qBittorrent pour utiliser les trackers privés avec les débrideurs tout en respectant les règles de ratio.
- Amélioration du cache communautaire public pour une couverture plus complète.

## Installation

Suivez ces étapes pour installer StreamFusion :

1. **Prérequis**
   - Assurez-vous d'avoir Docker et Docker Compose installés sur votre système.
   - Vous aurez besoin d'une clé API TMDB.

2. **Préparation**
   - Créez un nouveau dossier pour StreamFusion et placez-y le fichier `docker-compose.yml`.

3. **Configuration initiale**
   - Ouvrez le fichier `docker-compose.yml` dans un éditeur de texte.
   - Modifiez les variables d'environnement suivantes :
     - `SECRET_API_KEY`: Choisissez une clé API secrète pour StreamFusion.
     - `TMDB_API_KEY`: Entrez votre clé API TMDB.
   - Ajustez les autres paramètres selon vos besoins (par exemple, `TZ` pour le fuseau horaire).

4. **Lancement des services initiaux**
   - Ouvrez un terminal et naviguez jusqu'au dossier contenant le fichier `docker-compose.yml`.
   - Lancez d'abord Elasticsearch et Zilean avec la commande :
     ```
     docker-compose up -d elasticsearch zilean
     ```
   - **Note importante** : La première synchronisation de Zilean peut prendre entre 20 minutes et 1 heure selon les performances de votre machine. Cette opération consomme beaucoup de ressources. Assurez-vous d'avoir suffisamment de RAM et de CPU disponibles.

5. **Configuration de Jackett**
   - Une fois la synchronisation de Zilean terminée, lancez Jackett :
     ```
     docker-compose up -d jackett
     ```
   - Accédez à l'interface Jackett à l'adresse : `http://localhost:9117`
   - Configurez vos indexeurs et récupérez la clé API Jackett.

6. **Mise à jour du docker-compose.yml**
   - Retournez dans le fichier `docker-compose.yml`.
   - Mettez à jour la variable `JACKETT_API_KEY` avec la clé récupérée sur Jackett.

7. **Lancement de StreamFusion**
   - Lancez StreamFusion et les services restants :
     ```
     docker-compose up -d
     ```

8. **Configuration du Reverse Proxy**
   - Il est fortement recommandé de placer le conteneur StreamFusion derrière un reverse proxy pour une meilleure sécurité et gestion.
   - Vous pouvez utiliser l'un des reverse proxys suivants :
     - Nginx Proxy Manager
     - SWAG (Secure Web Application Gateway)
     - Traefik
   - Configurez le reverse proxy pour rediriger le trafic vers le port 8080 de StreamFusion.

9. **Accès**
   - Une fois le reverse proxy configuré, StreamFusion sera accessible via l'URL que vous aurez définie.

10. **Mise à jour**
    - Pour mettre à jour les conteneurs, exécutez :
      ```
      docker-compose pull
      docker-compose up -d
      ```

11. **Arrêt**
    - Pour arrêter tous les services, utilisez :
      ```
      docker-compose down
      ```

Note : Les dossiers nécessaires seront créés automatiquement par Docker. Assurez-vous d'avoir suffisamment d'espace disque disponible.

## Configuration

StreamFusion peut être configuré via des variables d'environnement. Voici les principales options de configuration :

### Légende
✅ : Requis
❌ : Optionnel

### Général

| Variable | Description | Valeur par défaut | Requis |
|----------|-------------|-------------------|--------|
| `WORKERS_COUNT` | Nombre de workers | 4 | ❌ |
| `PORT` | Port sur lequel le service s'exécute | 8080 | ❌ |
| `HOST` | Hôte sur lequel le service s'exécute | "0.0.0.0" | ❌ |
| `GUNICORN_TIMEOUT` | Timeout pour Gunicorn en secondes | 180 | ❌ |
| `AIOHTTP_TIMEOUT` | Timeout pour aiohttp en secondes | 7200 | ❌ |
| `PROXIED_LINK` | Proxifier les liens à travers le serveur | False | ❌ |
| `PLAYBACK_PROXY` | URL du proxy pour la lecture | None | ❌ |
| `SESSION_KEY` | Clé de session | (valeur par défaut fournie) | ✅ |
| `USE_HTTPS` | Utiliser HTTPS (True si reverse proxy utilisé) | False | ✅ |

### Logging

| Variable | Description | Valeur par défaut | Requis |
|----------|-------------|-------------------|--------|
| `LOG_LEVEL` | Niveau de log (NOTSET, DEBUG, INFO, WARNING, ERROR, FATAL) | INFO | ❌ |
| `LOG_PATH` | Chemin du fichier de log | "/app/config/logs/stream-fusion.log" | ❌ |
| `LOG_REDACTED` | Masquer les informations sensibles dans les logs | True | ❌ |

### Sécurité

| Variable | Description | Valeur par défaut | Requis |
|----------|-------------|-------------------|--------|
| `SECRET_API_KEY` | Clé API secrète pour l'authentification | None | ✅ |
| `SECURITY_HIDE_DOCS` | Cacher la documentation API | True | ❌ |

### Base de données

| Variable | Description | Valeur par défaut | Requis |
|----------|-------------|-------------------|--------|
| `DB_PATH` | Chemin de la base de données SQLite | "/app/config/stream-fusion.db" | ❌ |
| `DB_ECHO` | Activer l'echo SQL | False | ❌ |
| `DB_TIMEOUT` | Timeout de la base de données en secondes | 15 | ❌ |

### Redis

| Variable | Description | Valeur par défaut | Requis |
|----------|-------------|-------------------|--------|
| `REDIS_HOST` | Hôte Redis | "redis" | ❌ |
| `REDIS_PORT` | Port Redis | 6379 | ❌ |
| `REDIS_EXPIRATION` | Durée d'expiration du cache Redis en secondes | 604800 | ❌ |

### TMDB

| Variable | Description | Valeur par défaut | Requis |
|----------|-------------|-------------------|--------|
| `TMDB_API_KEY` | Clé API pour The Movie Database | None | ✅ |

### FlareSolverr

| Variable | Description | Valeur par défaut | Requis |
|----------|-------------|-------------------|--------|
| `FLARESOLVERR_HOST` | Hôte FlareSolverr | "localhost" | ❌ |
| `FLARESOLVERR_SHEMA` | Schéma pour FlareSolverr (http/https) | "http" | ❌ |
| `FLARESOLVERR_PORT` | Port FlareSolverr | 8191 | ❌ |

### Jackett

| Variable | Description | Valeur par défaut | Requis |
|----------|-------------|-------------------|--------|
| `JACKETT_HOST` | Hôte Jackett | "localhost" | ❌ |
| `JACKETT_SHEMA` | Schéma pour Jackett (http/https) | "http" | ❌ |
| `JACKETT_PORT` | Port Jackett | 9117 | ❌ |
| `JACKETT_API_KEY` | Clé API Jackett | None | ❌ |

### Zilean DMM API

| Variable | Description | Valeur par défaut | Requis |
|----------|-------------|-------------------|--------|
| `ZILEAN_API_KEY` | Clé API pour Zilean (optionnel) | None | ❌ |
| `ZILEAN_URL` | URL de l'API Zilean | None | ❌ |
| `ZILEAN_MAX_WORKERS` | Nombre maximum de workers pour Zilean | 4 | ❌ |
| `ZILEAN_POOL_CONNECTIONS` | Nombre de connexions dans le pool | 10 | ❌ |
| `ZILEAN_API_POOL_MAXSIZE` | Taille maximale du pool API | 10 | ❌ |
| `ZILEAN_MAX_RETRY` | Nombre maximum de tentatives | 3 | ❌ |

### YGGTorrent

| Variable | Description | Valeur par défaut | Requis |
|----------|-------------|-------------------|--------|
| `YGG_URL` | URL de YGGTorrent | `https://ygg.re` | ❌ |
| `YGG_USER` | Nom d'utilisateur YGGTorrent | None | ❌ |
| `YGG_PASS` | Mot de passe YGGTorrent | None | ❌ |
| `YGG_PASSKEY` | Passkey YGGTorrent | None | ❌ |
| `YGGFLIX_URL` | URL de YGGFlix | `https://yggflix.fr` | ❌ |
| `YGGFLIX_MAX_WORKERS` | Nombre maximum de workers pour YGGFlix | 4 | ❌ |

### Sharewood

| Variable | Description | Valeur par défaut | Requis |
|----------|-------------|-------------------|--------|
| `SHAREWOOD_URL` | URL de Sharewood | `https://www.sharewood.tv` | ❌ |
| `SHAREWOOD_MAX_WORKERS` | Nombre maximum de workers pour Sharewood | 4 | ❌ |
| `SHAREWOOD_PASSKEY` | Passkey Sharewood | None | ❌ |

### Cache public

| Variable | Description | Valeur par défaut | Requis |
|----------|-------------|-------------------|--------|
| `PUBLIC_CACHE_URL` | URL du cache public | `https://stremio-jackett-cacher.elfhosted.com/` | ❌ |

### Développement

| Variable | Description | Valeur par défaut | Requis |
|----------|-------------|-------------------|--------|
| `DEBUG` | Activer le mode debug | True | ❌ |
| `DEV_HOST` | Hôte de développement | "0.0.0.0" | ❌ |
| `DEV_PORT` | Port de développement | 8080 | ❌ |
| `DEVELOP` | Mode développement | True | ❌ |

### Version

| Variable | Description | Valeur par défaut | Requis |
|----------|-------------|-------------------|--------|
| `VERSION_PATH` | Chemin vers le fichier pyproject.toml | "/app/pyproject.toml" | ❌ |

Note : Les variables marquées comme requises (✅) doivent être configurées pour que StreamFusion fonctionne correctement. Les variables optionnelles (❌) peuvent être laissées à leur valeur par défaut ou ajustées selon vos besoins. Assurez-vous de gérer de manière sécurisée les variables sensibles, par exemple en utilisant des secrets Docker ou des variables d'environnement sécurisées.

## Utilisation

Une fois StreamFusion déployé et accessible derrière un reverse proxy, suivez ces étapes pour configurer et utiliser l'addon :

### Configuration initiale

1. Accédez au panel d'administration :
   - Ouvrez votre navigateur et allez à `https://votre-domaine.com/api/admin`
   - Utilisez la `SECRET_API_KEY` que vous avez configurée pour vous connecter au panel admin.

2. Création d'une clé API utilisateur :
   - Dans le panel admin, créez une nouvelle clé API pour chaque utilisateur.
   - Choisissez l'option "never expire" pour la durée de validité de la clé.

3. Configuration de l'addon :
   - Rendez-vous sur `https://votre-domaine.com`
   - Vous arriverez sur la page de configuration de StreamFusion.
   - Remplissez les informations demandées, y compris la clé API que vous venez de créer.

4. Installation dans Stremio :
   - Cliquez sur "Install" une fois la configuration terminée.
   - Vous serez redirigé vers Stremio, ou
   - Copiez le lien de configuration et collez-le dans la barre de recherche des plugins de Stremio.

### Configurer les métadonnées en français

Pour obtenir les métadonnées en français dans Stremio :

1. Ajoutez d'abord l'addon TMDB dans Stremio.
2. Ouvrez Stremio Web : https://web.stremio.com/
3. Allez sur la page des addons.
4. Appuyez sur F12 pour ouvrir la console du navigateur.
5. Copiez et collez le code fourni sur [ce post Reddit](https://www.reddit.com/r/StremioAddons/comments/1d8wbul/how_to_remove_cinemeta/) dans la console.
6. Exécutez le code pour supprimer Cinemeta.
7. (Optionnel) Vous pouvez réinstaller Cinemeta pour améliorer la réactivité de la recherche.

### Réorganiser l'ordre des plugins et catalogues

Pour personnaliser l'ordre d'affichage des plugins et catalogues dans Stremio :

1. Visitez [Stremio Addon Manager](https://addon-manager.dontwanttos.top/)
2. Utilisez cet outil pour réorganiser vos addons selon vos préférences.

### Conseils d'utilisation

- Assurez-vous de garder votre clé API secrète et de ne pas la partager.
- Vérifiez régulièrement les mises à jour de StreamFusion pour bénéficier des dernières fonctionnalités et corrections.
- En cas de problème, consultez les logs de StreamFusion pour identifier d'éventuelles erreurs.

## Contribution

Les contributions sont les bienvenues ! Veuillez vous référer à nos directives de contribution pour plus de détails.

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## Avertissement

Ce projet est destiné uniquement à des fins éducatives et de recherche. Les utilisateurs sont responsables de leur utilisation du logiciel et doivent se conformer aux lois locales sur le droit d'auteur et la propriété intellectuelle.

## Contact

[![Discord](https://img.shields.io/badge/Discord-Rejoignez%20nous%20sur%20SSD!-7289DA?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/ZhWvKVmTuh)

---

StreamFusion is a project derived from Stremio-Jackett, rewritten and improved to offer a better user experience and extended functionalities.