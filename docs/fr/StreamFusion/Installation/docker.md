# Installation de StreamFusion

Cette page détaille le processus d'installation de StreamFusion et de ses dépendances à l'aide de Docker Compose.

## Prérequis

Assurez-vous d'avoir rempli tous les prérequis mentionnés dans la [page des prérequis](prerequis.md).

## Étapes d'installation

### 1. Création du répertoire

Créez un nouveau répertoire pour la stack StreamFusion :

```bash
mkdir streamfusion && cd streamfusion
```

### 2. Téléchargement du fichier docker-compose.yml

Téléchargez le fichier `docker-compose.yml` depuis le dépôt GitHub :

```bash
curl -O https://raw.githubusercontent.com/votre-repo/streamfusion/main/docker-compose.yml
```

### 3. Création du fichier .env

Créez un fichier `.env` dans le même répertoire et ajoutez-y les variables d'environnement suivantes :

```bash
nano .env
```

Copiez et collez le contenu suivant, en remplaçant les valeurs par les vôtres :

```env
# StreamFusion
SECRET_API_KEY='<REDATED>'
TMDB_API_KEY='<REDATED>'
JACKETT_API_KEY='<Optional>'
RD_TOKEN='<Optional>'
AD_TOKEN='<Optional>'
YGG_PASSKEY='<Optional>'
SHAREWOOD_PASSKEY='<Optional>'
```

## Configuration des variables d'environnement

Voici une explication détaillée de chaque variable :

| Variable        | Description                                                           | Obligatoire |
|:----------------|:----------------------------------------------------------------------|:-----------:|
| `SECRET_API_KEY`| Clé secrète pour accéder au panneau d'administration.                 | Oui         |
| `TMDB_API_KEY`  | Votre clé API pour The Movie Database.                                | Oui         |
| `JACKETT_API_KEY`| Clé API pour Jackett, pour l'indexation des torrents.                | Non         |
| `RD_TOKEN`      | Token Real-Debrid pour un compte unique.                              | Non         |
| `AD_TOKEN`      | Token AllDebrid pour un compte unique.                                | Non         |
| `YGG_PASSKEY`   | Passkey YGGTorrent pour un compte unique.                             | Non         |
| `SHAREWOOD_PASSKEY`| Passkey Sharewood pour un compte unique.                           | Non         |

!!! warning "Sécurité"
    Ne partagez jamais vos clés API ou tokens. Assurez-vous que votre fichier `.env` n'est pas accessible publiquement.

## Lancement de la stack Docker Compose


!!! note "Initialisation et configuration"
    - Lors de l'initialisation, Zilean télécharge toutes les hashlist DMM et les indexe dans la base de données PostgreSQL.
    - Avec la configuration actuelle, optimisée pour les systèmes à faibles ressources, ce processus peut prendre entre 2 et 5 heures, selon la puissance du CPU de la machine.
    - Le fetching IMDB de Zilean est désactivé par défaut dans cette configuration pour gagner du temps et économiser les ressources.
    - Toutes ces options sont configurables. Pour plus de détails, consultez la section [Configuration avancée](#).
    
Une fois les fichiers `docker-compose.yml` et `.env` configurés, lancez la stack :

```bash
docker-compose up -d
```

Vérifiez que tous les conteneurs sont en cours d'exécution :

```bash
docker-compose ps
```

## Mise à jour et gestion

### Mise à jour des conteneurs

Pour mettre à jour les conteneurs de StreamFusion :

1. Tirez les dernières images :
   ```bash
   docker-compose pull
   ```

2. Redémarrez les conteneurs avec les nouvelles images :
   ```bash
   docker-compose up -d
   ```

### Gestion de l'installation

- **Arrêter la stack** : `docker-compose down`
- **Voir les logs** : `docker-compose logs -f [nom_du_service]`
- **Redémarrer un service spécifique** : `docker-compose restart [nom_du_service]`

!!! tip "Sauvegarde"
    Pensez à sauvegarder régulièrement vos fichiers `docker-compose.yml` et `.env`, ainsi que les volumes Docker si vous souhaitez conserver vos données.