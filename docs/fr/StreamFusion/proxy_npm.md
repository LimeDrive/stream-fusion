# Nginx Proxy Manager

Ce guide vous accompagnera dans la mise en place d'un reverse proxy pour StreamFusion en utilisant Nginx Proxy Manager et Cloudflare pour la gestion de domaine.

## Configuration du domaine avec Cloudflare

Avant de configurer le reverse proxy, vous devez configurer votre domaine avec Cloudflare.

!!! info "Documentation Cloudflare"
    Pour une guide détaillé sur la configuration de votre domaine chez Cloudflare, veuillez consulter la [documentation officielle de Cloudflare](https://developers.cloudflare.com/fundamentals/get-started/setup/add-site/).

!!! warning "Pacience"
    Si vous n'avez pas encore configuré votre domaine avec Cloudflare, la vérification de la propriété du domaine peut prendre quelques heures.


### Création des sous-domaines

Une fois votre domaine configuré chez Cloudflare, vous devez créer les sous-domaines nécessaires.

1. Obtenez l'adresse IP publique de votre VPS :
   ```bash
   curl ifconfig.me
   ```
   ou
   ```bash
   wget -qO- http://ipecho.net/plain | xargs echo
   ```

2. Dans le tableau de bord Cloudflare, allez dans la section "DNS".

3. Créez les enregistrements DNS suivants :

    #### Enregistrement A pour le domaine racine

    | Type | Nom | Contenu | Proxy status |
    |------|-----|---------|--------------|
    | A    | @   | [Votre adresse IP publique] | Proxied |
    | A    | www   | [Votre adresse IP publique] | Proxied |

    #### Enregistrements CNAME pour les sous-domaines

    | Type  | Nom          | Contenu | Proxy status |
    |-------|--------------|---------|--------------|
    | CNAME | proxy        | @       | Proxied      |
    | CNAME | streamfusion | @       | Proxied      |
    | CNAME | jackett      | @       | Proxied      |

    !!! warning "Proxy Cloudflare"
        Assurez-vous que le statut du proxy est activé (orange) pour tous vos enregistrements afin de bénéficier de la protection Cloudflare.

**Voici à quoi devrait ressembler votre configuration DNS final :**

## Installation de Nginx Proxy Manager

### Création du répertoire pour le reverse proxy

1. Connectez-vous à votre VPS via SSH.
2. Créez un nouveau répertoire pour Nginx Proxy Manager :
   ```bash
   mkdir nginx-proxy-manager && cd nginx-proxy-manager
   ```

### Configuration du docker-compose.yml

Créez un fichier `docker-compose.yml` dans ce répertoire :

```bash
nano docker-compose.yml
```

Copiez et collez le contenu suivant :

```yaml
services:
  app:
    image: 'jc21/nginx-proxy-manager:latest'
    restart: unless-stopped
    ports:
      - '80:80'
      - '81:81'
      - '443:443'
    volumes:
      - ./data:/data
      - ./letsencrypt:/etc/letsencrypt
    networks:
      - proxy_network

networks:
  proxy_network:
    external: true
```

!!! note "Réseau Docker"
    Assurez-vous que le réseau `proxy_network` a été créé précédemment comme indiqué dans le guide d'installation de StreamFusion.

### Lancement de Nginx Proxy Manager

Démarrez Nginx Proxy Manager avec la commande suivante :

```bash
docker-compose up -d
```

## Configuration de Nginx Proxy Manager

### Accès à l'interface d'administration

1. Ouvrez votre navigateur et accédez à `http://<votre_ip_vps>:81`.
2. Connectez-vous avec les identifiants par défaut :
   - Email : `admin@example.com`
   - Mot de passe : `changeme`

!!! danger "Sécurité"
    Changez immédiatement le mot de passe et l'email après votre première connexion !

### Création des règles de proxy

Pour chaque service (StreamFusion, Jackett), suivez ces étapes :

1. Cliquez sur "Proxy Hosts" puis "Add Proxy Host".

2. Remplissez les champs :

    - Domain Names : Entrez le sous-domaine complet (ex: streamfusion.votredomaine.com)
    - Scheme : http
    - Forward Hostname / IP : Nom du service Docker (ex: streamfusion)
    - Forward Port : Port du service (ex: 8080 pour StreamFusion)

3. Dans l'onglet "SSL", sélectionnez "Request a new SSL Certificate" et cochez "Force SSL".

4. Cliquez sur "Save".

!!! tip "Noms de services Docker"
    Assurez-vous que les noms de services dans votre `docker-compose.yml` de StreamFusion correspondent aux Forward Hostname que vous utilisez ici.
    Il en vas de même pour les ports, vous les trouverais dans la partit expose de votre `docker-compose.yml` de streamfusion.

**Voici quelques captures d'écran pour vous guider :**

## Vérification et test

Après avoir configuré tous vos services :

1. Accédez à vos services via leurs sous-domaines respectifs (ex: https://streamfusion.votredomaine.com).
2. Vérifiez que la connexion est sécurisée (HTTPS) et que le certificat SSL est valide.

!!! success "Configuration terminée"
    Votre reverse proxy est maintenant configuré et sécurisé. Vos services sont accessibles via HTTPS et protégés par Cloudflare.

## Maintenance et sécurité

- Vérifiez régulièrement les mises à jour de Nginx Proxy Manager.
- Surveillez les logs pour détecter toute activité suspecte.