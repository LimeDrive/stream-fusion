# StreamFusion Post-Installation

This guide will walk you through the initial configuration steps of StreamFusion after its deployment behind a reverse proxy.

## Accessing the Admin Panel

The first step is to access the StreamFusion admin panel to perform the initial configuration.

1. Open your preferred web browser.
2. Navigate to the following URL:
   ```
   https://your-domain.com/api/admin
   ```
   
    !!! note "Custom URL"
        Replace `your-domain.com` with the domain you've configured for StreamFusion.

3. You'll be prompted to authenticate. Use the `SECRET_API_KEY` you defined during the initial installation.

    !!! warning "API Key Security"
        The `SECRET_API_KEY` is highly sensitive. Never share it and ensure it's stored securely.

## Creating a User API Key

Once logged into the admin panel, you need to create an API key for each StreamFusion user.

1. Click on "New API Key" or a similar button.
2. Fill in the required information:

   - User's name
   - Select "never expire" for the key's validity duration
   
    !!! tip "Key Management"
        While "never expire" is convenient, consider periodically renewing keys for enhanced security.

3. Confirm the key creation.
4. Carefully note down the generated API key, as it will be necessary for addon configuration.

## Configuring the StreamFusion Addon

After obtaining a user API key, you can proceed with configuring the StreamFusion addon.

1. In your browser, go to:
   ```
   https://your-domain.com
   ```
2. You'll be directed to the StreamFusion configuration page.
3. Fill in the requested information:

   - User API key (the one you just created)
   - Other parameters according to your preferences

    !!! info "Optional Parameters"
        Depending on the StreamFusion version, you might have additional options like content provider selection, quality filters, etc.

4. Carefully check all settings before confirming.

## Installation in Stremio

Once the addon configuration is complete, you can install it in Stremio.

### Method 1: Direct Installation

1. After completing the configuration, click the "Install" button.
2. If a Stremio app is installed on your device, it should open automatically and prompt you to add the addon.
3. Confirm the installation in Stremio.

### Method 2: Manual Installation

If direct installation doesn't work or if you're configuring StreamFusion on a different device from where Stremio is installed:

1. After configuration, copy the link with the dedicated button.
2. Open Stremio on your device.
3. Go to the addons section (usually represented by a puzzle icon).
4. Look for an option to add an addon manually, often symbolized by a "+" or "Add addon".
5. Paste the addon URL you copied.
6. Confirm adding the addon.

!!! success "Successful Installation"
    Once installed, you should see StreamFusion in your list of Stremio addons. You can now enjoy its content!

## Troubleshooting

If you encounter issues during the installation or use of StreamFusion:

- Verify that your reverse proxy is correctly configured.
- Ensure that the API key used is valid and has not expired on your admin panel.
- Check StreamFusion logs to identify any errors.
- Check your internet connection and make sure Stremio is up to date.

!!! tip "Community Support"
    Don't hesitate to consult StreamFusion forums or support channels for additional help.

By following these steps, you should have successfully configured StreamFusion and integrated it into your Stremio installation. Enjoy your enhanced streaming experience!