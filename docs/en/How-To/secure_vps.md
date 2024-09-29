# VPS Installation Guide

## Introduction

This detailed guide will walk you through the installation and configuration of a VPS (Virtual Private Server). We will emphasize security and best practices throughout the process.

!!! info "Choosing a VPS provider"
    For this guide, we will use a VPS costing €1.20/month from [IONOS](https://www.ionos.fr/serveur-cloud). However, many providers offer similar services at competitive prices.

!!! tip "Important selection criteria"
    - Fixed public IPv4 address
    - Unlimited or generous bandwidth
    - Support for KVM virtualization or similar
    - Good reputation in terms of reliability and support

## Initial VPS Configuration

### Initial SSH Connection

The first step is to connect to your VPS via SSH.

1. Retrieve the IP address and credentials from your provider's interface or confirmation email.
2. Open a terminal and connect as root:

   ```bash
   ssh root@<ip_address>
   ```

3. Enter the provided password when prompted.

!!! warning "Security"
    This initial connection uses a password. We will quickly secure this with SSH keys.

### System Update

Start by updating your system:

```bash
apt update && apt upgrade -y
```

!!! note "Possible interactions"
    If configuration messages appear, generally validate with "OK" or choose the default options.

### VPS Restart

To apply all updates, restart your VPS:

```bash
reboot
```

!!! info "Reconnection"
    After restarting, wait a few minutes, then reconnect via SSH.

### Hostname Configuration

Customize your server's identity:

1. Modify the hostname:
   ```bash
   hostnamectl set-hostname <your_hostname>
   ```

2. Update the `/etc/hosts` file:
   ```bash
   nano /etc/hosts
   ```
   Add or modify the line:
   ```
   127.0.1.1 <your_hostname>
   ```

## Securing SSH Access

### Generating and Deploying SSH Keys

1. On your local machine, generate an SSH key pair:
   ```bash
   ssh-keygen -t ed25519 -C "my_vps"
   ```

2. Copy the public key to the VPS:
   ```bash
   ssh-copy-id root@<ip_address>
   ```

3. Test the connection with the new key:
   ```bash
   ssh root@<ip_address>
   ```

!!! success "Successful Authentication"
    If you connect without a password, the SSH key configuration is successful.

### Installing ZSH and Oh My Zsh

Enhance your command-line experience:

1. Install ZSH:
   ```bash
   apt install zsh -y
   ```

2. Install Oh My Zsh:
   ```bash
   sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
   ```

3. Customize your ZSH configuration:
   ```bash
   nano ~/.zshrc
   ```

!!! tip "Customization"
    Explore available themes and addons for Oh My Zsh to optimize your productivity.

## Creating a Non-Root User

For better security, create a non-root user:

1. Add a new user:
   ```bash
   adduser <username>
   ```

2. Grant sudo privileges:
   ```bash
   usermod -aG sudo <username>
   ```

3. Configure SSH access for this user:
   ```bash
   ssh-copy-id <username>@<ip_address>
   ```

## Firewall Configuration

### Opening Necessary Ports

Configure the UFW firewall to allow only necessary services:

```bash
ufw allow 51820/udp  # WireGuard
ufw allow 443/tcp    # HTTPS
ufw allow 80/tcp     # HTTP
ufw allow <custom_ssh_port>/tcp  # Custom SSH
```

Enable the firewall:

```bash
ufw enable
```

!!! warning "Caution"
    Make sure you have correctly configured the SSH port before enabling the firewall to avoid locking yourself out.

### IONOS Panel Configuration

Don't forget to configure the same firewall rules in the IONOS management interface.

## SSH Security Hardening

Strengthen the SSH configuration:

1. Remove the cloud-init configuration:
   ```bash
   rm -rf /etc/ssh/sshd_config.d/50-cloud-init.conf
   ```

2. Edit the SSH configuration file:
   ```bash
   nano /etc/ssh/sshd_config
   ```

3. Modify the following parameters:
   ```
   Port <custom_ssh_port>
   PermitRootLogin prohibit-password
   PasswordAuthentication no
   PermitEmptyPasswords no
   ```

4. Restart the SSH service:
   ```bash
   systemctl restart sshd
   ```

!!! danger "Caution"
    Test the new SSH configuration in a new session before closing your current session to avoid any lockout.

## Installing Tailscale

Tailscale offers an easy-to-use VPN solution based on WireGuard.

Follow the [official Tailscale documentation](https://tailscale.com/kb/1085/install-debian/) for installation on Debian.

## Installing Docker

Install Docker to facilitate application deployment:

1. Download and run the installation script:
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   ```

2. Add your user to the Docker group:
   ```bash
   sudo usermod -aG docker $USER
   ```

!!! note "Activating changes"
    Log out and log back in for the group changes to take effect.

## Installing CrowdSec

CrowdSec is an open-source collaborative security solution.

Follow the [official CrowdSec documentation](https://doc.crowdsec.net/docs/getting_started/installation/) for installation.

## Conclusion

Your VPS is now securely configured and ready to host StreamFusion and other services. Remember to:

- Perform regular updates
- Monitor logs and security alerts
- Regularly backup your important data and configurations

!!! tip "Next steps"
    Consider exploring other security and monitoring tools to further strengthen your infrastructure.