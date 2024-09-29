# Versions auto-hébergées de Stremio et de ses addons

## addons Stremio auto-hébergés (Selfhosted)

Les addons auto-hébergés pour Stremio offrent aux utilisateurs un contrôle accru sur leurs sources de contenu et leurs fonctionnalités. Ils permettent de personnaliser l'expérience Stremio tout en gardant le contrôle sur les données et la confidentialité.

### Fonctionnement des addons auto-hébergés

Les addons auto-hébergés fonctionnent comme des serveurs web locaux qui répondent aux requêtes de l'application Stremio. Voici les principes de base :

1. **API HTTP** : Les addons exposent une API HTTP que Stremio peut interroger.
2. **Manifeste** : Chaque addon fournit un manifeste décrivant ses capacités et les types de contenu qu'il peut gérer.
3. **Handlers** : Les addons implémentent des handlers pour répondre aux différentes requêtes de Stremio (catalogue, métadonnées, flux, etc.).
4. **Réseau local** : Les addons peuvent être hébergés sur le réseau local de l'utilisateur, offrant des temps de réponse rapides et un contrôle total.

### Avantages des addons auto-hébergés

- **Confidentialité** : Les données restent sur votre réseau local.
- **Personnalisation** : Vous pouvez adapter l'addon à vos besoins spécifiques.
- **Performance** : Potentiellement plus rapide car hébergé localement.
- **Contrôle** : Vous gérez les mises à jour et la configuration.


## Versions auto-hébergées de Stremio

Stremio offre la possibilité d'auto-héberger certaines de ses composantes, ce qui permet un meilleur contrôle et une personnalisation accrue de l'expérience de streaming. Il existe principalement deux approches pour l'auto-hébergement de Stremio : le serveur de streaming et l'interface web.

### Stremio Streaming Server

Le Stremio Streaming Server est une version allégée du serveur de streaming de Stremio qui peut être exécutée indépendamment de l'application de bureau.

### Caractéristiques

- Fonctionne comme un serveur autonome
- Permet de diffuser du contenu sur votre réseau local ou à distance
- Compatible avec Docker pour un déploiement facile