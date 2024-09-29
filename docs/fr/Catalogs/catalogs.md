# Stremio Catalog Providers

![Stremio Catalog Providers](./images/image-jic6p-29-09-2024.jpg)

## Description

Stremio Catalog Providers est un addon optimisé pour le contenu français, conçu pour enrichir l'expérience utilisateur de Stremio en ajoutant de nouveaux catalogues. Cette addon utilise The Movie Database (TMDB) comme source principale d'informations, tout en intégrant les API de Rating Poster Database (RPDB) et FanArt pour améliorer la présentation visuelle et les métadonnées.

!!! info "Développement actif"
    Cette addon est activement développé par un développeur français, assurant une attention particulière aux besoins de la communauté francophone.

## Fonctionnalités clés

### Gestion dynamique des plateformes de streaming
- Gère plus de 600 plateformes de streaming
- S'adapte aux configurations utilisateur via la page de paramètres de l'addon

### Catalogues de films et séries
- Propose des catalogues de contenus populaires et récents
- Affiche les titres et affiches dans la langue configurée par l'utilisateur

### Contenu spécifique par région
- Agrège le contenu spécifique à chaque région (ex: Netflix FR, Netflix US) dans un catalogue unifié
- Assure l'accès au contenu localisé pour les utilisateurs

### Filtrage par âge (Catalogue Jeunesse)
- Filtre le contenu selon des tranches d'âge basées sur les certifications américaines
- Exclut les genres inappropriés
- Des directives détaillées sont accessibles via l'icône "?" dans les paramètres

### Filtrage avancé des catalogues
- Permet de filtrer les catalogues par genre, note et année de sortie

### Affichage personnalisable des catalogues
- Permet d'organiser l'ordre d'affichage des catalogues via la page de configuration de l'addon

### Recommandations et titres similaires
- Affiche les contenus recommandés et similaires directement sur la page du contenu

### Intégration Trakt
- Synchronise l'historique de visionnage Trakt avec Stremio
- Marque les éléments visionnés dans les catalogues avec un emoji personnalisable
- Synchronisation automatique quotidienne (intervalle personnalisable)
- Rafraîchissement automatique du token pour éviter la ré-authentification
- Permet de marquer manuellement le contenu comme visionné sur Trakt depuis Stremio

### Intégration RPDB
- Fournit des affiches de films et séries avec leurs notes

### Intégration FanArt
- Remplace les titres par des logos dans la langue sélectionnée (ou en anglais par défaut)

### Scraping progressif
- Précharge les pages de contenu à venir pendant le défilement pour améliorer les temps de chargement

### Gestion de cache personnalisable
- Durée de cache des catalogues ajustable via une variable d'environnement
- Cache des affiches RPDB personnalisable pour réduire la charge de l'API

## Source des données

Toutes les données des catalogues proviennent de TMDB, conformément à leurs conditions d'utilisation. Ce produit utilise l'API TMDB mais n'est ni approuvé ni certifié par TMDB.

## Remerciements

Un grand merci au développeur français de Stremio Catalog Providers pour son travail acharné et son dévouement à améliorer l'expérience Stremio pour la communauté francophone et internationale. Votre contribution est grandement appréciée !