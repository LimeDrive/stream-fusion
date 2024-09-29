# Hardware and Software Configuration
To successfully self-host StreamFusion, you must ensure you have the appropriate environment. This section details the necessary hardware and software prerequisites.

## Server or VPS
A properly configured and secured dedicated server or VPS (Virtual Private Server) is essential for hosting StreamFusion. Here's a comparative table of minimum and recommended specifications:

| Component | Minimum | Recommended |
| :-------- | :------ | :--------- |
| RAM | 8 GB | 16 GB |
| CPU | 4 cores | 8 cores |
| Storage | 40 GB SSD | 40 GB SSD |
| Bandwidth | 1 Gbps | 1 Gbps |

!!! note "Note"
    The recommended specifications will offer better performance and allow handling a larger number of simultaneous users.

!!! warning "Advice"
    Secure your server by following security best practices. Consult our guide [Securing a VPS](../../How-To/secure_vps.md) for more information.

## Docker Environment
StreamFusion uses Docker to simplify service deployment and management. Make sure you have the following installed on your server:

- Docker
- Docker Compose

!!! info "Installation"
    Consult the [official Docker documentation](https://docs.docker.com/get-docker/) for installation instructions specific to your operating system.

## Domain Name
A dedicated domain name is necessary to access your StreamFusion instance:

- Choose a domain name representative of your project
- Ensure it's easy to remember and type
- Check its availability with a trusted registrar

!!! example "Example"
    `streamfusion.yourdomain.com` or `stream.yourdomain.com`

## Cloudflare Account
Cloudflare is used for managing your domain name and offers additional benefits:

- DDoS protection
- Free SSL/TLS
- Performance optimization

!!! success "Steps"
    1. Create a free account on [Cloudflare](https://www.cloudflare.com/)
    2. Add your domain to Cloudflare
    3. Update your domain's DNS servers with those provided by Cloudflare

## Debrid Accounts
To fully use StreamFusion's features, you'll need accounts with debrid services. Here's a comparative table of the main debridders supported by StreamFusion:

| Debridder | Description | Pricing (approximate) |
|-----------|-------------|------------------------|
| RealDebrid | Popular service with wide compatibility | Starting at €3/month |
| AllDebrid | Reliable alternative with additional features | Starting at €3/month |

!!! warning "Beware of IP blocks"
    Debridders may block server IP addresses. To circumvent this issue, especially with AllDebrid, we'll use a proxy called Warp.

!!! tip "Installing Warp"
    Warp will be automatically installed and configured via Docker Compose to handle potential IP blocks.

!!! info "Configuring debrid accounts"
    Configuring a debrid account is not mandatory on StreamFusion. Two configuration options are possible:

    1. **Centralized configuration**:

        - If an account is configured in the environment variable, all users will use the same account.
        - In this case, all video streams will be automatically proxied by the application to avoid debridder bans.

    2. **Individual configuration**:

        - If no account is configured in the environment variables, each user can connect their own debrid accounts on the configuration page.
        - In this case, streaming links are not proxied by the application.

!!! warning "Important recommendation"
    The developer strongly advises using one account per user. It is recommended not to put debridder tokens or APIs in the environment variables, but rather let users connect themselves with their own accounts.

!!! danger "Respect for terms of use"
    Using a single account for all users does not comply with the Terms of Service of debridders. As these services are offered at low prices, it's important not to abuse them to ensure their longevity.

## Download Sources
Users will need accounts on torrent trackers to access download sources. Here are those integrated into StreamFusion:

- YGGTorrent
- Sharewood

!!! important "Passkey configuration"
    Tracker passkeys are not mandatory during the initial installation of StreamFusion. However, their management influences the user experience:
    
    - If a passkey is provided in the environment variables during configuration, it will be used for all addon users.
    - If no passkey is provided, each user will need to configure their own passkey on the addon configuration page. Thus, each user will use their own account on each tracker.
    
    This flexibility allows either a centralized configuration or user-by-user customization according to your needs.

## Mandatory Dependencies

!!! tip "Automatic installation"
    Mandatory dependencies will be automatically installed with Docker Compose.

StreamFusion requires the following dependencies to function correctly:

| Dependency | Description |
|------------|-------------|
| PostgreSQL | Relational database |
| Redis      | In-memory data storage system |
| Warp       | HTTP/HTTPS proxy to handle blocks |

## Optional Dependencies

!!! tip "Possible customization"
    Optional dependencies will be installed by default with Docker Compose. You can modify the `docker-compose.yml` file to disable them if necessary.

The following dependencies are optional but can enhance StreamFusion's functionalities:

- **Zilean**: For indexing DebridMediaManager hashlists
- **Jackett**: For indexing torrent sites
- **Prowlarr**: *(NOT AVAILABLE - under development)*

!!! note "Resource optimization"
    To minimize dependencies, this stack uses a PostgreSQL database and a Redis server for all addons. StreamFusion automatically manages the creation of its database and tables. You can therefore connect it to an existing database if you have one.

## Next Steps
Once you've verified that you have all the prerequisites, you can proceed to install StreamFusion. Consult the [Docker Install](docker_install.md) section for detailed instructions.