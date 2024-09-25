# Pré-requis pour StreamFusion

Cette page détaille les éléments nécessaires pour auto-héberger StreamFusion ainsi que les dépendances requises pour son bon fonctionnement.

## Configuration matérielle et logicielle

Pour auto-héberger StreamFusion, vous aurez besoin des éléments suivants :

### **Serveur ou VPS** :

- Configuré et sécurisé
- Spécifications minimales :
    - 8 Go de RAM
    - 4 cœurs de processeur

### **Environnement Docker** :
  - Docker installé
  - Docker-compose installé

### **Nom de domaine** :
  - Un nom de domaine dédié à votre instance StreamFusion

### **Compte Cloudflare** :
  - Compte gratuit pour la gestion de votre nom de domaine

## Dépendances obligatoires

StreamFusion nécessite les dépendances suivantes pour fonctionner correctement :

| Dépendance | Description |
|------------|-------------|
| PostgreSQL | Base de données relationnelle |
| Redis      | Système de stockage de données en mémoire |

## Dépendances optionnelles

Les dépendances suivantes sont optionnelles mais peuvent améliorer les fonctionnalités de StreamFusion :

- **Zilean** : Pour l'indexation des hashlists de DébridMediaManager
- **Jackett** : Pour l'indexation des sites de torrents
- **Prowlarr** : *(NON DISPONIBLE - en cours de développement)*

!!! note
    Afin de minimiser les dépendances, cette stack utilise une base de données PostgreSQL et un serveur Redis pour l'ensemble des plugins. StreamFusion gère automatiquement la création de sa base de données et de ses tables. Vous pouvez donc le connecter à une base déjà existante.

## Étapes suivantes

Une fois que vous avez vérifié que vous disposez de tous les pré-requis, vous pouvez passer à l'installation de StreamFusion. Consultez la section [Docker Install](docker.md) pour les instructions détaillées.