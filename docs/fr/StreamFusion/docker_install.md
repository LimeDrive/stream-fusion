# Installation de StreamFusion

Cette page détaille le processus d'installation de StreamFusion et de ses dépendances à l'aide de Docker Compose, offrant une méthode simple et efficace pour déployer l'ensemble de la stack.

## Prérequis

Avant de commencer l'installation, assurez-vous d'avoir rempli tous les prérequis mentionnés dans la [page des prérequis](prerequis.md).

!!! tip "Gestion automatique des dépendances"
    Docker Compose se chargera d'installer automatiquement toutes les dépendances, qu'elles soient obligatoires ou optionnelles, simplifiant grandement le processus de déploiement.

## Étapes d'installation

Suivez ces étapes pour installer StreamFusion sur votre système.

### 1. Création du réseau Docker pour le proxy

Avant de configurer les services, nous allons créer un réseau Docker dédié pour le proxy. Ce réseau permettra une communication sécurisée entre les différents conteneurs de votre stack StreamFusion.

Créez le réseau Docker nommé `proxy_network` avec la commande suivante :

```bash
docker network create proxy_network
```

!!! note "Importance du réseau proxy"
    La création d'un réseau dédié pour le proxy offre plusieurs avantages :

    - Isolation : Les services peuvent communiquer entre eux sans être exposés directement à l'extérieur.
    - Sécurité : Vous pouvez contrôler précisément quels conteneurs peuvent communiquer entre eux.
    - Flexibilité : Facilite l'ajout ou la suppression de services sans perturber le reste de la stack.

!!! tip "Vérification du réseau"
    Vous pouvez vérifier que le réseau a été correctement créé avec la commande :
    ```bash
    docker network ls
    ```
    Vous devriez voir `proxy_network` dans la liste des réseaux disponibles.

### 2. Création du répertoire

Commencez par créer un nouveau répertoire dédié à la stack StreamFusion :

```bash
mkdir streamfusion && cd streamfusion
```

!!! note "Organisation"
    Cette étape permet de garder tous les fichiers liés à StreamFusion dans un seul endroit, facilitant la gestion et les futures mises à jour.

### 3. Téléchargement du fichier docker-compose.yml

Téléchargez le fichier `docker-compose.yml` depuis le dépôt GitHub officiel :

```bash
curl -O https://raw.githubusercontent.com/LimeDrive/stream-fusion/master/deploy/docker-compose.yml
```

!!! warning "Vérification du fichier"
    Après le téléchargement, il est recommandé de vérifier le contenu du fichier pour s'assurer qu'il n'a pas été altéré durant le transfert.

### 4. Création du fichier .env

Créez un fichier `.env` dans le même répertoire pour stocker les variables d'environnement :

```bash
nano .env
```

Copiez et collez le contenu suivant, en remplaçant les valeurs par les vôtres :

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

!!! danger "Sécurité des données sensibles"
    Ne partagez jamais vos clés API ou tokens. Assurez-vous que votre fichier `.env` n'est pas accessible publiquement et considérez l'utilisation d'un gestionnaire de secrets pour une sécurité accrue.

## Configuration des variables d'environnement

Le tableau suivant détaille chaque variable d'environnement :

| Variable | Description | Obligatoire |
|:----------------|:----------------------------------------------------------------------|:-----------:|
| `SECRET_API_KEY`| Clé secrète pour l'accès au panneau d'administration | Oui |
| `TMDB_API_KEY` | Clé API pour The Movie Database | Oui |
| `JACKETT_API_KEY`| Clé API pour Jackett (indexation des torrents) | Non |
| `RD_TOKEN` | Token Real-Debrid pour un compte unique | Non |
| `AD_TOKEN` | Token AllDebrid pour un compte unique | Non |
| `YGG_PASSKEY` | Passkey YGGTorrent pour un compte unique | Non |
| `SHAREWOOD_PASSKEY`| Passkey Sharewood pour un compte unique | Non |

!!! tip "Obtention des clés API"
    Pour obtenir les clés API nécessaires :
    
    - TMDB : Créez un compte sur [The Movie Database](https://www.themoviedb.org/) et générez une clé API dans les paramètres de votre compte.
    - Jackett : Installez Jackett et trouvez la clé API dans l'interface web.
    - Token Real-Debrid : Ici : [Real-Debrid Token](https://real-debrid.com/apitoken).
    - Token AllDebrid : Suivre le tuto ici : [Tuto AllDebrid](../../How-To/apikey_alldebrid.md).

## Lancement de la stack Docker Compose

Une fois les fichiers `docker-compose.yml` et `.env` configurés, lancez la stack :

```bash
docker compose up -d
```

Vérifiez que tous les conteneurs sont en cours d'exécution :

```bash
docker compose ps
```

!!! note "Initialisation et configuration"
    - Lors de l'initialisation, Zilean télécharge toutes les hashlist DMM et les indexe dans la base de données PostgreSQL.
    - Avec la configuration actuelle, optimisée pour les systèmes à faibles ressources, ce processus peut prendre entre 2 et 5 heures, selon la puissance du CPU de la machine.
    - Le fetching IMDB de Zilean est désactivé par défaut dans cette configuration pour gagner du temps et économiser les ressources.
    - Toutes ces options sont configurables. Pour plus de détails, consultez la section [Configuration avancée](#).

!!! tip "Suivi de l'initialisation"
    Vous pouvez suivre le processus d'initialisation en temps réel avec la commande :
    ```bash
    docker compose logs -f zilean
    ```

## Mise à jour et gestion

Maintenez votre installation de StreamFusion à jour et gérez-la efficacement.

### Mise à jour des conteneurs

Pour mettre à jour les conteneurs de StreamFusion :

1. Tirez les dernières images :
    ```bash
    docker compose pull
    ```

2. Redémarrez les conteneurs avec les nouvelles images :
    ```bash
    docker compose up -d
    ```

!!! info "Fréquence des mises à jour"
    Il est recommandé de vérifier les mises à jour au moins une fois par semaine pour bénéficier des dernières fonctionnalités et correctifs de sécurité.

### Gestion de l'installation

Commandes utiles pour gérer votre installation :

- **Arrêter la stack** : `docker compose down`
- **Voir les logs** : `docker compose logs -f [nom_du_service]`
- **Redémarrer un service spécifique** : `docker compose restart [nom_du_service]`

!!! tip "Sauvegarde"
    Pensez à sauvegarder régulièrement vos fichiers `docker-compose.yml` et `.env`, ainsi que les volumes Docker si vous souhaitez conserver vos données. Vous pouvez automatiser ce processus avec un script de sauvegarde.

!!! example "Script de sauvegarde basique"
    ```bash
    #!/bin/bash
    BACKUP_DIR="/chemin/vers/backups"
    mkdir -p $BACKUP_DIR
    cp docker-compose.yml .env $BACKUP_DIR
    docker compose exec postgres pg_dump -U postgres > $BACKUP_DIR/database_backup.sql
    ```

En suivant ces instructions, vous aurez une installation robuste et bien gérée de StreamFusion. N'hésitez pas à consulter la documentation pour des configurations plus avancées ou des optimisations spécifiques à votre cas d'utilisation.
