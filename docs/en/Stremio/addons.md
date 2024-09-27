![!Stremio Addons](./images/image-1rqo9-24-09-2024.png)

# The Stremio Plugin System

Stremio uses a plugin (or add-on) system to extend its functionalities and provide content. These plugins allow users to customize their experience by adding new content sources, additional features, and integrations with other services.

## Types of Stremio Plugins

Stremio supports several types of plugins, each with a specific role:

### 1. Content Plugins
These plugins provide content sources for movies, TV series, live channels, etc.
**Examples**:

- Torrentio (for public torrents)
- Netflix (official integration)
- StreamFusion (advanced addon for French-language content)

### 2. Metadata Plugins
They provide additional information about the content, such as descriptions, ratings, actors, etc.
**Examples**:

- Cinemata
- TMDB (The Movie Database)

### 3. Subtitle Plugins
These plugins add subtitle sources for content.
**Examples**:

- OpenSubtitles
- Subscene

### 4. Catalog Plugins
They add new catalogs or content categories to Stremio.
**Examples**:

- Stremio-Addon-Catalogs (Supported by a French dev)
- Stremio-Addon-Sagas (for movie sagas)
- Anime Kitsu (for anime catalogs)

### 5. Utility Plugins
These plugins add additional functionalities to Stremio.
**Examples**:

- Trakt (to track what you watch)
- DLNA (for streaming to other devices)

## How Plugins Work

Stremio plugins function as web APIs. When a user searches for content or information, Stremio queries the installed plugins to obtain relevant results. Plugins can be hosted locally or on remote servers.

## Installing Plugins

Installing plugins in Stremio is simple and can be done in several ways:

1. **Via the official catalog**:
   - Open Stremio and click on the puzzle icon in the top right corner.
   - Browse available plugins and click "Install" for those that interest you.

2. **Via a URL**:
   - If you have a plugin URL, you can add it by clicking "Add addon" in the plugins menu.
   - Paste the URL and click "Add".

3. **Via a local file**:
   - For locally developed plugins, you can install them using their local URL (usually `http://localhost:PORT`).

## Plugin Development

Developers can create their own Stremio plugins using the official SDK. The process typically involves:

1. Using the Stremio SDK (available in JavaScript/Node.js).
2. Defining a manifest that describes the plugin's capabilities.
3. Implementing handlers for various functionalities (streaming, metadata, etc.).
4. Deploying the plugin on a publicly accessible server.

## Security and Legal Considerations

- Official plugins are generally safe, but third-party plugins may present risks.
- Some plugins may provide access to copyrighted content. Users should be aware of the legal implications of using such plugins.

## Conclusion

Stremio's plugin system is what makes the application so versatile and popular. It allows users to access a wide range of content and features, while offering developers the opportunity to create and share their own extensions.