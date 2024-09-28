# Post-installation de StreamFusion

Ce guide vous accompagnera à travers les étapes de configuration initiale de StreamFusion après son déploiement derrière un reverse proxy.

## Accès au panel d'administration

La première étape consiste à accéder au panel d'administration de StreamFusion pour effectuer la configuration initiale.

1. Ouvrez votre navigateur web préféré.
2. Naviguez vers l'URL suivante :
    ```
    https://votre-domaine.com/api/admin
    ```

    !!! note "URL personnalisée"
        Remplacez `votre-domaine.com` par le domaine que vous avez configuré pour StreamFusion.

3. Vous serez invité à vous authentifier. Utilisez la `SECRET_API_KEY` que vous avez définie lors de l'installation initiale.

    !!! warning "Sécurité de la clé API"
        La `SECRET_API_KEY` est hautement sensible. Ne la partagez jamais et assurez-vous qu'elle est stockée de manière sécurisée.

## Création d'une clé API utilisateur

Une fois connecté au panel d'administration, vous devez créer une clé API pour chaque utilisateur de StreamFusion.

1. Cliquez sur "New API Key" ou un bouton similaire.
2. Remplissez les informations requises :

   - Nom de l'utilisateur
   - Sélectionnez "never expire" pour la durée de validité de la clé
   
    !!! tip "Gestion des clés"
        Bien que "never expire" soit pratique, envisagez de renouveler périodiquement les clés pour une sécurité accrue.

3. Confirmez la création de la clé.
4. Notez soigneusement la clé API générée, car elle sera nécessaire pour la configuration de l'addon.


## Configuration de l'addon StreamFusion

Après avoir obtenu une clé API utilisateur, vous pouvez procéder à la configuration de l'addon StreamFusion.

1. Dans votre navigateur, accédez à :
   ```
   https://votre-domaine.com
   ```
2. Vous serez dirigé vers la page de configuration de StreamFusion.
3. Remplissez les informations demandées :

   - Clé API utilisateur (celle que vous venez de créer)
   - Autres paramètres selon vos préférences

    !!! info "Paramètres optionnels"
        Selon la version de StreamFusion, vous pourriez avoir des options supplémentaires comme la sélection de fournisseurs de contenu, des filtres de qualité, etc.

4. Vérifiez attentivement tous les paramètres avant de confirmer.

## Installation dans Stremio

Une fois la configuration de l'addon terminée, vous pouvez l'installer dans Stremio.

### Méthode 1 : Installation directe

1. Après avoir complété la configuration, cliquez sur le bouton "Install".
2. Si une app Stremio est installé sur votre appareil, elle devrait s'ouvrir automatiquement et vous proposer d'ajouter l'addon.
3. Confirmez l'installation dans Stremio.

### Méthode 2 : Installation manuelle

Si l'installation directe ne fonctionne pas ou si vous configurez StreamFusion sur un appareil différent de celui où Stremio est installé :

1. Après la configuration, Copiez le lien avec le boutton dédié.
2. Ouvrez Stremio sur votre appareil.
3. Allez dans la section des addons (généralement représentée par une icône de puzzle).
4. Recherchez une option pour ajouter un addon manuellement, souvent symbolisée par un "+" ou "Ajouter un addon".
5. Collez l'URL de l'addon que vous avez copiée.
6. Confirmez l'ajout de l'addon.

!!! success "Installation réussie"
    Une fois installé, vous devriez voir StreamFusion dans la liste de vos addons Stremio. Vous pouvez maintenant profiter de son contenu !

## Dépannage

Si vous rencontrez des problèmes lors de l'installation ou de l'utilisation de StreamFusion :

- Vérifiez que votre reverse proxy est correctement configuré.
- Assurez-vous que la clé API utilisée est valide et n'a pas expiré sur votre panel admin.
- Consultez les logs de StreamFusion pour identifier d'éventuelles erreurs.
- Vérifiez votre connexion internet et assurez-vous que Stremio est à jour.

!!! tip "Support communautaire"
    N'hésitez pas à consulter les forums ou les canaux de support de StreamFusion pour obtenir de l'aide supplémentaire.

En suivant ces étapes, vous devriez avoir configuré avec succès StreamFusion et l'avoir intégré à votre installation Stremio. Profitez de votre expérience de streaming améliorée !
