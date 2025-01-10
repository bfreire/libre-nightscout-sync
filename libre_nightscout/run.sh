#!/usr/bin/with-contenv bashio

# Ensure data directory exists
mkdir -p /data

bashio::log.info "Starting configuration..."

# Get config values
LIBRELINK_USERNAME=$(bashio::config 'librelink_username')
LIBRELINK_PASSWORD=$(bashio::config 'librelink_password')
LIBRELINK_REGION=$(bashio::config 'librelink_region')
NIGHTSCOUT_URL=$(bashio::config 'nightscout_url')
NIGHTSCOUT_API_TOKEN=$(bashio::config 'nightscout_api_token')
SYNC_INTERVAL=$(bashio::config 'sync_interval')

# Debug output (masking sensitive data)
bashio::log.info "Configuration values:"
bashio::log.info "LIBRELINK_USERNAME: ${LIBRELINK_USERNAME}"
bashio::log.info "LIBRELINK_REGION: ${LIBRELINK_REGION}"
bashio::log.info "NIGHTSCOUT_URL: ${NIGHTSCOUT_URL}"
bashio::log.info "SYNC_INTERVAL: ${SYNC_INTERVAL}"

# Export environment variables
export LIBRELINK_USERNAME
export LIBRELINK_PASSWORD
export LIBRELINK_REGION
export NIGHTSCOUT_URL
export NIGHTSCOUT_API_TOKEN
export SYNC_INTERVAL

bashio::log.info "Configuration loaded. Starting sync service..."

# Create options file if it doesn't exist
if [ ! -f "/data/options.json" ]; then
    bashio::log.info "Creating options.json file..."
    echo "{}" > /data/options.json
    chmod 644 /data/options.json
fi

# Start the Python script with error handling
bashio::log.info "Launching Python script..."
if python3 -u /app/libre_nightscout_sync.py 2>&1; then
    bashio::log.info "Python script exited normally"
else
    bashio::log.error "Python script failed with exit code $?"
fi 