# Guide d'utilisation du Stremio Add-on Manager

## Prérequis

!!! important "Plugins requis"
    Avant d'utiliser le Stremio Add-on Manager, assurez-vous d'avoir installé et configuré les plugins suivants sur votre compte Stremio :

    * TMDB (plugin officiel)
    * Stream-Fusion
    * Catalogs
    * Trakt

## Étapes d'utilisation

### Étape 1 : Connexion au manager

1. Rendez-vous sur la page de votre plugin Stremio Addon Manager.
2. Connectez votre compte Stremio (Step 0 sur l'interface).

![Conn](./images/image-5lutq-29-09-2024(1).png)

!!! tip "Astuce"
    Assurez-vous d'utiliser les mêmes identifiants que pour votre application Stremio.

### Étape 2 : Chargement des add-ons

1. Cliquez sur "Load addons" (Step 1 sur l'interface).

![Load](./images/image-jix10-29-09-2024.png)

!!! note "Note"
    Cette action va récupérer tous les add-ons installés sur votre compte Stremio.

### Étape 3 : Déverrouillage et configuration

1. Dans la Step 2 de l'interface, cliquez sur "Unlock Addons".
    * Cela débloque la suppression des plugins nativement bloqués par Stremio.
2. Toujours dans la Step 2, cliquez sur "Setup TMDB".
    * Cette action configure le plugin officiel TMDB pour gérer les métadonnées dans Stremio, fournissant du contenu en français.

![Unlock](./images/image-1ahs1-29-09-2024(1).png)

!!! info "Information"
    La configuration TMDB est cruciale pour obtenir des métadonnées en français dans Stremio.

### Étape 4 : Personnalisation des add-ons

Dans la Step 3 de l'interface :

1. Configurez l'ordre de vos plugins.
    * L'ordre influencera également l'ordre des catalogues sur la page d'accueil de Stremio.
2. Utilisez la configuration avancée pour :
    * Renommer les catalogues
    * Supprimer les catalogues indésirables de certains plugins
    * Supprimer les plugins indésirables

![Customize](./images/image-qbzjb-29-09-2024.png)

!!! warning "Attention"
    Soyez prudent lors de la suppression de plugins ou de catalogues. Certains peuvent être essentiels au bon fonctionnement de Stremio.

### Étape 5 : Synchronisation avec Stremio

1. Dans la Step 4, cliquez sur "Sync to Stremio".
    * Cela met à jour les modifications effectuées dans l'étape précédente.

![Sync](./images/image-na5z3-29-09-2024.png)

## Finalisation

!!! important "Redémarrage nécessaire"
    Pour que les modifications prennent effet, redémarrez complètement votre client Stremio.

## Résolution de problèmes

!!! tip "Problèmes de métadonnées en français"
    Si vous rencontrez des problèmes avec les métadonnées en français :
    
    1. Vérifiez que le plugin TMDB officiel est bien installé sur votre compte.
    2. Retournez sur le Stremio Add-on Manager.
    3. Cliquez à nouveau sur "Setup TMDB" dans la Step 2.

## Configuration avancée

!!! note "Édition des manifestes"
    La configuration avancée permet d'éditer complètement le manifeste des plugins. Cependant, cette fonctionnalité est recommandée uniquement pour les utilisateurs ayant une bonne compréhension du fonctionnement des manifestes de plugins Stremio.

!!! warning "Précaution"
    L'édition incorrecte des manifestes peut entraîner des dysfonctionnements des plugins. Procédez avec prudence et sauvegardez vos configurations avant toute modification importante.