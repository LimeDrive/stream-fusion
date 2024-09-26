# Configuration matérielle et logicielle

Pour auto-héberger StreamFusion avec succès, vous devez vous assurer de disposer de l'environnement adéquat. Cette section détaille les prérequis matériels et logiciels nécessaires.

## Serveur ou VPS

Un serveur dédié ou un VPS (Virtual Private Server) correctement configuré et sécurisé est essentiel pour héberger StreamFusion. Voici un tableau comparatif des spécifications minimales et recommandées :

| Composant | Minimum | Recommandé |
| :-------- | :------ | :--------- |
| RAM | 8 Go | 16 Go |
| CPU | 4 cœurs | 8 cœurs |
| Stockage | 40 Go SSD | 40 Go SSD |
| Bande passante | 1 Gbps | 1 Gbps |

!!! note "Note"
    Les spécifications recommandées offriront une meilleure performance et permettront de gérer un plus grand nombre d'utilisateurs simultanés.

!!! warning "Conseil"
    Sécurisez votre serveur en suivant les bonnes pratiques de sécurité. Consultez notre guide [Sécuriser un VPS](../../How-To/secure_vps.md) pour plus d'informations.


## Environnement Docker

StreamFusion utilise Docker pour simplifier le déploiement et la gestion des services. Assurez-vous d'avoir les éléments suivants installés sur votre serveur :

- Docker
- Docker Compose

!!! info "Installation"
    Consultez la [documentation officielle de Docker](https://docs.docker.com/get-docker/) pour les instructions d'installation spécifiques à votre système d'exploitation.

## Nom de domaine

Un nom de domaine dédié est nécessaire pour accéder à votre instance StreamFusion :

- Choisissez un nom de domaine représentatif de votre projet
- Assurez-vous qu'il soit facile à retenir et à taper
- Vérifiez sa disponibilité auprès d'un registrar de confiance

!!! example "Exemple"
    `streamfusion.votredomaine.com` ou `stream.votredomaine.com`

## Compte Cloudflare

Cloudflare est utilisé pour la gestion de votre nom de domaine et offre des avantages supplémentaires :

- Protection DDoS
- SSL/TLS gratuit
- Optimisation des performances

!!! success "Étapes"
    1. Créez un compte gratuit sur [Cloudflare](https://www.cloudflare.com/)
    2. Ajoutez votre domaine à Cloudflare
    3. Mettez à jour les serveurs DNS de votre domaine avec ceux fournis par Cloudflare

En suivant ces recommandations, vous disposerez d'une base solide pour héberger votre instance StreamFusion de manière efficace et sécurisée.

## Dépendances obligatoires

!!! tip "Installation Docker-Compose"
    Les dépendances obligatoires seront installées automatiquement avec Docker Compose.

StreamFusion nécessite les dépendances suivantes pour fonctionner correctement :

| Dépendance | Description |
|------------|-------------|
| PostgreSQL | Base de données relationnelle |
| Redis      | Système de stockage de données en mémoire |

## Dépendances optionnelles

!!! tip "Installation Docker-Compose"
    Les dépendances optionelles seront installées automatiquement avec Docker Compose.
    Mais vous pouvez toujour modifier le fichier `docker-compose.yml` pour les désactiver.

Les dépendances suivantes sont optionnelles mais peuvent améliorer les fonctionnalités de StreamFusion :

- **Zilean** : Pour l'indexation des hashlists de DébridMediaManager
- **Jackett** : Pour l'indexation des sites de torrents
- **Prowlarr** : *(NON DISPONIBLE - en cours de développement)*

!!! note
    Afin de minimiser les dépendances, cette stack utilise une base de données PostgreSQL et un serveur Redis pour l'ensemble des plugins. StreamFusion gère automatiquement la création de sa base de données et de ses tables. Vous pouvez donc le connecter à une base déjà existante.

## Étapes suivantes

Une fois que vous avez vérifié que vous disposez de tous les pré-requis, vous pouvez passer à l'installation de StreamFusion. Consultez la section [Docker Install](docker_install.md) pour les instructions détaillées.