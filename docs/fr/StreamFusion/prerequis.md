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

## Comptes de débrideurs
Pour utiliser pleinement les fonctionnalités de StreamFusion, vous aurez besoin de comptes chez des services de débridage. Voici un tableau comparatif des principaux débrideurs supporté par StreamFusion :

| Débrideur | Description | Tarifs (approximatifs) |
|-----------|-------------|------------------------|
| RealDebrid | Service populaire avec une large compatibilité | À partir de 3€/mois |
| AllDebrid | Alternative fiable avec des fonctionnalités supplémentaires | À partir de 3€/mois |

!!! warning "Attention aux blocages IP"
    Les débrideurs peuvent bloquer les adresses IP des serveurs. Pour contourner ce problème, notamment avec AllDebrid, nous utiliserons un proxy appelé Warp.

!!! tip "Installation de Warp"
    Warp sera automatiquement installé et configuré via Docker Compose pour gérer les éventuels blocages IP.

!!! info "Configuration des comptes de débrideurs"
    La configuration d'un compte de débrideur n'est pas obligatoire sur StreamFusion. Deux options de configuration sont possibles :

    1. **Configuration centralisée** :

        - Si un compte est configuré en variable d'environnement, tous les utilisateurs utiliseront le même compte.
        - Dans ce cas, tous les flux vidéo seront automatiquement proxifiés par l'application pour éviter les bannissements des débrideurs.

    2. **Configuration individuelle** :

        - Si aucun compte n'est configuré dans les variables d'environnement, chaque utilisateur pourra connecter ses propres comptes de débrideur sur la page de configuration.
        - Dans ce cas, les liens de streaming ne sont pas proxifiés par l'application.

!!! warning "Recommandation importante"
    Le développeur conseille fortement d'utiliser un compte par utilisateur. Il est recommandé de ne pas mettre les tokens ou API des débrideurs dans les variables d'environnement, mais plutôt de laisser les utilisateurs se connecter eux-mêmes avec leurs propres comptes.

!!! danger "Respect des conditions d'utilisation"
    L'utilisation d'un seul compte pour tous les utilisateurs ne respecte pas les conditions d'utilisation (Terms of Service) des débrideurs. Ces services étant proposés à bas prix, il est important de ne pas en abuser afin d'assurer leur pérennité.

## Sources de téléchargement
Les utilisateurs auront besoin de comptes sur des trackers torrents pour accéder aux sources de téléchargement. Voici ceux qui sont intégrés à StreamFusion :

- YGGTorrent
- Sharewood

!!! important "Configuration des passkeys"
    Les passkeys des trackers ne sont pas obligatoires lors de l'installation initiale de StreamFusion. Cependant, leur gestion influence l'expérience utilisateur :
    
    - Si une passkey est fournie dans les variables d'environnement lors de la configuration, elle sera utilisée pour tous les utilisateurs de l'addon.
    - Si aucune passkey n'est fournie, chaque utilisateur devra configurer sa propre passkey sur la page de configuration de l'addon. Ainsi, chaque utilisateur utilisera son propre compte sur chaque tracker.
    
    Cette flexibilité permet soit une configuration centralisée, soit une personnalisation par utilisateur selon vos besoins.

## Dépendances obligatoires

!!! tip "Installation automatique"
    Les dépendances obligatoires seront installées automatiquement avec Docker Compose.

StreamFusion nécessite les dépendances suivantes pour fonctionner correctement :

| Dépendance | Description |
|------------|-------------|
| PostgreSQL | Base de données relationnelle |
| Redis      | Système de stockage de données en mémoire |
| Warp       | Proxy HTTP/HTTPS pour gérer les blocages |

## Dépendances optionnelles

!!! tip "Personnalisation possible"
    Les dépendances optionnelles seront installées par défaut avec Docker Compose. Vous pouvez modifier le fichier `docker-compose.yml` pour les désactiver si nécessaire.

Les dépendances suivantes sont optionnelles mais peuvent améliorer les fonctionnalités de StreamFusion :

- **Zilean** : Pour l'indexation des hashlists de DébridMediaManager
- **Jackett** : Pour l'indexation des sites de torrents
- **Prowlarr** : *(NON DISPONIBLE - en cours de développement)*

!!! note "Optimisation des ressources"
    Afin de minimiser les dépendances, cette stack utilise une base de données PostgreSQL et un serveur Redis pour l'ensemble des addons. StreamFusion gère automatiquement la création de sa base de données et de ses tables. Vous pouvez donc le connecter à une base déjà existante si vous en avez une.

## Étapes suivantes
Une fois que vous avez vérifié que vous disposez de tous les pré-requis, vous pouvez passer à l'installation de StreamFusion. Consultez la section [Docker Install](docker_install.md) pour les instructions détaillées.