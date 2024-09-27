# Self-hosted Versions of Stremio and Its Plugins

## Self-hosted Stremio Plugins

Self-hosted plugins for Stremio offer users increased control over their content sources and functionalities. They allow for customization of the Stremio experience while maintaining control over data and privacy.

### How Self-hosted Plugins Work

Self-hosted plugins function as local web servers that respond to requests from the Stremio application. Here are the basic principles:

1. **HTTP API**: Plugins expose an HTTP API that Stremio can query.
2. **Manifest**: Each plugin provides a manifest describing its capabilities and the types of content it can handle.
3. **Handlers**: Plugins implement handlers to respond to various Stremio requests (catalog, metadata, streams, etc.).
4. **Local Network**: Plugins can be hosted on the user's local network, offering fast response times and total control.

### Advantages of Self-hosted Plugins

- **Privacy**: Data remains on your local network.
- **Customization**: You can adapt the plugin to your specific needs.
- **Performance**: Potentially faster as it's locally hosted.
- **Control**: You manage updates and configuration.

## Self-hosted Versions of Stremio

Stremio offers the possibility to self-host some of its components, allowing for better control and increased customization of the streaming experience. There are mainly two approaches to self-hosting Stremio: the streaming server and the web interface.

### Stremio Streaming Server

The Stremio Streaming Server is a lightweight version of Stremio's streaming server that can be run independently of the desktop application.

### Features

- Functions as a standalone server
- Allows streaming content on your local network or remotely
- Compatible with Docker for easy deployment