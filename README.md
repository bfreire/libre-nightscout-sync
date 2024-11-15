# LibreLink Up to Nightscout Sync

A Python script that synchronizes glucose data between LibreLink Up and Nightscout. This tool allows you to automatically fetch glucose readings from LibreLink Up and upload them to your Nightscout instance.

## Features

- Automatic synchronization between LibreLink Up and Nightscout
- Duplicate entry prevention
- Trend arrow support
- Easy configuration via environment variables
- Home Assistant integration support

## Prerequisites

- Python 3.7 or higher
- LibreLink Up account
- Nightscout instance
- (Optional) Home Assistant instance

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/libre-nightscout-sync.git
cd libre-nightscout-sync
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project directory with your credentials:

```env
LIBRELINK_USERNAME=your.email@example.com
LIBRELINK_PASSWORD=your_password
LIBRELINK_REGION=EU  # EU or US
NIGHTSCOUT_URL=https://your-nightscout-instance.herokuapp.com
NIGHTSCOUT_API_TOKEN=your-api-secret
```

### Region Settings
- Use `EU` for European accounts
- Use `US` for United States accounts

### Nightscout API Token
Your Nightscout API token should be either:
- Your API_SECRET if you're using authentication
- Any string matching your ENABLE/DISABLE settings if you're not using authentication

## Usage

### Basic Usage

Run the script manually:
```bash
python libre_nightscout_sync.py
```

Expected output:
```
Validating Nightscout API connection...
Successfully authenticated with LibreLink Up
Found 1 patient connection
Successfully uploaded 3 new readings to Nightscout
Sync completed successfully!
```

### Automated Usage

#### Using Cron (Linux/macOS)

To run the script every 5 minutes:

1. Open your crontab:
```bash
crontab -e
```

2. Add the following line:
```bash
*/5 * * * * cd /path/to/libre-nightscout-sync && /usr/bin/python3 libre_nightscout_sync.py >> /path/to/libre-nightscout-sync/sync.log 2>&1
```

#### Using Task Scheduler (Windows)

1. Open Task Scheduler
2. Create a new Basic Task
3. Set the trigger to run every 5 minutes
4. Action: Start a program
5. Program/script: `python`
6. Arguments: `libre_nightscout_sync.py`
7. Start in: `C:\path\to\libre-nightscout-sync`

### Docker Usage

1. Build the Docker image:
```bash
docker build -t libre-nightscout-sync .
```

2. Run the container:
```bash
docker run --env-file .env libre-nightscout-sync
```

Or using docker-compose:

```yaml
version: '3'
services:
  libre-sync:
    build: .
    env_file: .env
    restart: unless-stopped
```

### Home Assistant Integration

You can integrate this script with Home Assistant using the Scripts extension and Automations. This method is clean and allows you to manage the script directly from Home Assistant's interface.

#### Setup in Home Assistant

1. In your Home Assistant configuration directory, create a new directory structure:
```bash
config/
└── scripts/
    └── libre_nightscout_sync/
        ├── libre_nightscout_sync.py
        └── .env
```

2. Copy the `libre_nightscout_sync.py` script and create the `.env` file in this directory.

3. Install required Python packages in Home Assistant:
```bash
pip3 install requests python-dotenv
```

#### Create the Script

1. In Home Assistant, go to **Configuration** → **Scripts** and create a new script:
```yaml
alias: Libre Nightscout Sync
sequence:
  - service: shell_command.libre_nightscout_sync
    data: {}
mode: single
icon: mdi:diabetes
```

2. Add the shell command to your `configuration.yaml`:
```yaml
shell_command:
  libre_nightscout_sync: "python3 /config/scripts/libre_nightscout_sync/libre_nightscout_sync.py"
```

#### Create the Automation

1. Go to **Configuration** → **Automations** and create a new automation:
```yaml
alias: "Sync Libre to Nightscout Every 5 Minutes"
description: "Automatically sync Libre glucose readings to Nightscout"
trigger:
  - platform: time_pattern
    minutes: "/5"
condition: []
action:
  - service: script.libre_nightscout_sync
    data: {}
mode: single
```

This will:
- Run the sync every 5 minutes
- Use the script we created
- Handle errors gracefully

You can also add conditions or adjust the timing based on your needs.

#### Testing

1. Test the script manually by running the script from Home Assistant:
   - Go to **Developer Tools** → **Services**
   - Select `script.libre_nightscout_sync`
   - Click **Call Service**

2. Check Home Assistant logs for any errors:
   - Go to **Configuration** → **Logs**
   - Look for entries containing "libre_nightscout_sync"

#### Monitoring

You can create a sensor to monitor the sync status:

```yaml
template:
  - sensor:
      - name: "Libre Sync Status"
        state: >
          {% if states.automation.sync_libre_to_nightscout_every_5_minutes.last_triggered %}
            {% set time_diff = as_timestamp(now()) - as_timestamp(states.automation.sync_libre_to_nightscout_every_5_minutes.last_triggered) %}
            {% if time_diff < 360 %}
              Online
            {% else %}
              Offline
            {% endif %}
          {% else %}
            Unknown
          {% endif %}
```

This will show:
- "Online" if the sync ran in the last 6 minutes
- "Offline" if it's been more than 6 minutes
- "Unknown" if it hasn't run yet

## Troubleshooting

### Common Issues

1. Authentication Errors:
```
Error: Authentication failed: Invalid credentials
```
Solution: Verify your LibreLink Up username and password in the .env file

2. Region Errors:
```
Error: Network error during authentication
```
Solution: Make sure your LIBRELINK_REGION matches your account region (EU/US)

3. Nightscout Connection:
```
Error: Failed to validate Nightscout API connection
```
Solution: Check your NIGHTSCOUT_URL format (should include https://) and API token

### Logs

To enable detailed logging:
```bash
python libre_nightscout_sync.py > sync.log 2>&1
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- LibreLink Up for providing glucose data
- Nightscout for their amazing open-source project
- Home Assistant community for integration support