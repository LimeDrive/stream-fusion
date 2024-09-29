# Self-hosted Versions of Stremio and Its addons

## Self-hosted Stremio addons

Self-hosted addons for Stremio offer users increased control over their content sources and functionalities. They allow for customization of the Stremio experience while maintaining control over data and privacy.

### How Self-hosted addons Work

Self-hosted addons function as local web servers that respond to requests from the Stremio application. Here are the basic principles:

1. **HTTP API**: addons expose an HTTP API that Stremio can query.
2. **Manifest**: Each addon provides a manifest describing its capabilities and the types of content it can handle.
3. **Handlers**: addons implement handlers to respond to various Stremio requests (catalog, metadata, streams, etc.).
4. **Local Network**: addons can be hosted on the user's local network, offering fast response times and total control.

### Advantages of Self-hosted addons

- **Privacy**: Data remains on your local network.
- **Customization**: You can adapt the addon to your specific needs.
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