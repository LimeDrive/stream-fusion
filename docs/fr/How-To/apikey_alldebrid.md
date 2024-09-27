# Création d'une API Key AllDebrid

Ce guide vous aidera à créer une API key AllDebrid spécifiquement pour votre installation StreamFusion. Cette clé permettra à StreamFusion d'interagir de manière sécurisée avec votre compte AllDebrid.

## Prérequis

- Un compte AllDebrid actif
- Accès à un navigateur web

!!! note "Importance de l'API Key"
    Une API key dédiée à StreamFusion vous permet de contrôler et de révoquer l'accès indépendamment de vos autres applications, améliorant ainsi la sécurité de votre compte AllDebrid.

## Étapes de création de l'API Key

Suivez ces étapes pour générer votre API key AllDebrid pour StreamFusion :

### 1. Connexion à votre compte AllDebrid

1. Ouvrez votre navigateur et accédez au [site officiel d'AllDebrid](https://alldebrid.com/).
2. Cliquez sur "Se connecter" en haut à droite de la page.
3. Entrez vos identifiants et connectez-vous à votre compte.

!!! tip "Sécurité du compte"
    Assurez-vous d'utiliser un mot de passe fort et unique pour votre compte AllDebrid. Activez l'authentification à deux facteurs si disponible.

### 2. Génération de la clé API

1. Dans la section APIKEYS tout en haut :
![APIKEYS](./images/image-n0vw4-26-09-2024.jpg)
2. Dans la section "Créer une clé API" remplissez le formulaire avec `streamfusion`
![Créer une clé API](./images/image-a27gm-26-09-2024.png)

!!! warning "Nom de la clé API"
    Sur AllDebrid le noms des clés API sont important, pour un bon fonctionnement de StreamFusion, il est obligatoire de nommer la clé `streamfusion`.

### 3. Intégration avec StreamFusion

Si vous avez bien suivie les étapes précédentes, vous avez maintenant une nouvelle clé API AllDebrid nommée `streamfusion`. Vous pouvez maintenant l'intégrer à votre installation StreamFusion.

![Clé API](./images/image-lwthq-26-09-2024.png)

1. Ouvrez le fichier `.env` de votre installation StreamFusion.
2. Trouvez la ligne `AD_TOKEN=` et collez votre nouvelle clé API juste après le signe égal.
3. Sauvegardez le fichier `.env`.

!!! success "Configuration terminée"
    Votre clé API AllDebrid est maintenant correctement configurée pour être utilisée avec StreamFusion !