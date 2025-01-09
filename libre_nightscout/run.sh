#!/usr/bin/with-contenv bashio

# Ensure data directory exists
mkdir -p /data

# Get config values
LIBRELINK_USERNAME=$(bashio::config 'librelink_username')
LIBRELINK_PASSWORD=$(bashio::config 'librelink_password')
LIBRELINK_REGION=$(bashio::config 'librelink_region')
NIGHTSCOUT_URL=$(bashio::config 'nightscout_url')
NIGHTSCOUT_API_TOKEN=$(bashio::config 'nightscout_api_token')
SYNC_INTERVAL=$(bashio::config 'sync_interval')

# Export environment variables
export LIBRELINK_USERNAME
export LIBRELINK_PASSWORD
export LIBRELINK_REGION
export NIGHTSCOUT_URL
export NIGHTSCOUT_API_TOKEN

bashio::log.info "Starting LibreLink Up to Nightscout Sync..."

# Create options file if it doesn't exist
if [ ! -f "/data/options.json" ]; then
    echo "{}" > /data/options.json
    chmod 644 /data/options.json
fi

# Start the Python script
python3 /app/libre_nightscout_sync.py 