# Guide d'installation d'une VPS

## Introduction

Ce guide détaillé vous accompagnera dans l'installation et la configuration d'un serveur VPS (Virtual Private Server). Nous mettrons l'accent sur la sécurité et les bonnes pratiques tout au long du processus.

!!! info "Choix du fournisseur VPS"
    Pour ce guide, nous utiliserons un VPS à 1,20€/mois chez [IONOS](https://www.ionos.fr/serveur-cloud). Cependant, de nombreux fournisseurs offrent des services similaires à des prix compétitifs.

!!! tip "Critères de sélection importants"
    - Adresse IPv4 publique fixe
    - Bande passante illimitée ou généreuse
    - Support de la virtualisation KVM ou similaire
    - Bonne réputation en termes de fiabilité et de support

## Configuration initiale du VPS

### Connexion SSH initiale

La première étape consiste à se connecter à votre VPS via SSH.

1. Récupérez l'adresse IP et les identifiants dans l'interface de votre fournisseur ou dans l'email de confirmation.
2. Ouvrez un terminal et connectez-vous en tant que root :

   ```bash
   ssh root@<ip_address>
   ```

3. Entrez le mot de passe fourni lorsque vous y êtes invité.

!!! warning "Sécurité"
    Cette connexion initiale utilise un mot de passe. Nous allons rapidement sécuriser cela avec des clés SSH.

### Mise à jour du système

Commencez par mettre à jour votre système :

```bash
apt update && apt upgrade -y
```

!!! note "Interactions possibles"
    Si des messages de configuration apparaissent, validez généralement par "OK" ou choisissez les options par défaut.

### Redémarrage du VPS

Pour appliquer toutes les mises à jour, redémarrez votre VPS :

```bash
reboot
```

!!! info "Reconnexion"
    Après le redémarrage, attendez quelques minutes, puis reconnectez-vous via SSH.

### Configuration du hostname

Personnalisez l'identité de votre serveur :

1. Modifiez le hostname :
   ```bash
   hostnamectl set-hostname <votre_hostname>
   ```

2. Mettez à jour le fichier `/etc/hosts` :
   ```bash
   nano /etc/hosts
   ```
   Ajoutez ou modifiez la ligne :
   ```
   127.0.1.1 <votre_hostname>
   ```

## Sécurisation de l'accès SSH

### Génération et déploiement des clés SSH

1. Sur votre machine locale, générez une paire de clés SSH :
   ```bash
   ssh-keygen -t ed25519 -C "ma_vps"
   ```

2. Copiez la clé publique sur le VPS :
   ```bash
   ssh-copy-id root@<ip_address>
   ```

3. Testez la connexion avec la nouvelle clé :
   ```bash
   ssh root@<ip_address>
   ```

!!! success "Authentification réussie"
    Si vous vous connectez sans mot de passe, la configuration des clés SSH est réussie.

### Installation de ZSH et Oh My Zsh

Améliorez votre expérience en ligne de commande :

1. Installez ZSH :
   ```bash
   apt install zsh -y
   ```

2. Installez Oh My Zsh :
   ```bash
   sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
   ```

3. Personnalisez votre configuration ZSH :
   ```bash
   nano ~/.zshrc
   ```

!!! tip "Personnalisation"
    Explorez les thèmes et addons disponibles pour Oh My Zsh pour optimiser votre productivité.

## Création d'un utilisateur non-root

Pour une meilleure sécurité, créez un utilisateur non-root :

1. Ajoutez un nouvel utilisateur :
   ```bash
   adduser <username>
   ```

2. Accordez-lui les privilèges sudo :
   ```bash
   usermod -aG sudo <username>
   ```

3. Configurez l'accès SSH pour cet utilisateur :
   ```bash
   ssh-copy-id <username>@<ip_address>
   ```

## Configuration du pare-feu

### Ouverture des ports nécessaires

Configurez le pare-feu UFW pour autoriser uniquement les services nécessaires :

```bash
ufw allow 51820/udp  # WireGuard
ufw allow 443/tcp    # HTTPS
ufw allow 80/tcp     # HTTP
ufw allow <custom_ssh_port>/tcp  # SSH personnalisé
```

Activez le pare-feu :

```bash
ufw enable
```

!!! warning "Attention"
    Assurez-vous d'avoir correctement configuré le port SSH avant d'activer le pare-feu pour éviter de vous bloquer l'accès.

### Configuration du panel IONOS

N'oubliez pas de configurer les mêmes règles de pare-feu dans l'interface de gestion IONOS.

## Sécurisation de SSH

Renforcez la configuration SSH :

1. Supprimez la configuration cloud-init :
   ```bash
   rm -rf /etc/ssh/sshd_config.d/50-cloud-init.conf
   ```

2. Éditez le fichier de configuration SSH :
   ```bash
   nano /etc/ssh/sshd_config
   ```

3. Modifiez les paramètres suivants :
   ```
   Port <custom_ssh_port>
   PermitRootLogin prohibit-password
   PasswordAuthentication no
   PermitEmptyPasswords no
   ```

4. Redémarrez le service SSH :
   ```bash
   systemctl restart sshd
   ```

!!! danger "Attention"
    Testez la nouvelle configuration SSH dans une nouvelle session avant de fermer votre session actuelle pour éviter tout verrouillage.

## Installation de Tailscale

Tailscale offre une solution VPN facile à utiliser basée sur WireGuard.

Suivez la [documentation officielle de Tailscale](https://tailscale.com/kb/1085/install-debian/) pour l'installation sur Debian.

## Installation de Docker

Installez Docker pour faciliter le déploiement d'applications :

1. Téléchargez et exécutez le script d'installation :
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   ```

2. Ajoutez votre utilisateur au groupe Docker :
   ```bash
   sudo usermod -aG docker $USER
   ```

!!! note "Activation des changements"
    Déconnectez-vous et reconnectez-vous pour que les changements de groupe prennent effet.

## Installation de CrowdSec

CrowdSec est une solution de sécurité collaborative open-source.

Suivez la [documentation officielle de CrowdSec](https://doc.crowdsec.net/docs/getting_started/installation/) pour l'installation.

## Conclusion

Votre VPS est maintenant configuré de manière sécurisée et prêt à héberger StreamFusion et d'autres services. N'oubliez pas de :

- Effectuer des mises à jour régulières
- Surveiller les logs et les alertes de sécurité
- Sauvegarder régulièrement vos données et configurations importantes

!!! tip "Prochaines étapes"
    Envisagez d'explorer d'autres outils de sécurité et de monitoring pour renforcer davantage votre infrastructure.