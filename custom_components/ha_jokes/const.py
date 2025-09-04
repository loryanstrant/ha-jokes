"""Constants for the Dad Jokes integration."""

DOMAIN = "ha_jokes"
NAME = "Dad Jokes"
VERSION = "1.0.4"

# API Configuration
API_URL = "https://icanhazdadjoke.com"
API_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Home Assistant Dad Jokes Integration",
}

# Default Configuration
DEFAULT_REFRESH_INTERVAL = 5  # minutes
MIN_REFRESH_INTERVAL = 1     # minute
MAX_REFRESH_INTERVAL = 1440  # 24 hours in minutes

# Sensor Configuration
SENSOR_NAME = "Dad Joke"
SENSOR_ICON = "mdi:emoticon-happy-outline"

# Configuration Keys
CONF_REFRESH_INTERVAL = "refresh_interval"

# Attributes
ATTR_JOKE = "joke"
ATTR_JOKE_ID = "joke_id"
ATTR_LAST_UPDATED = "last_updated"
ATTR_REFRESH_INTERVAL = "refresh_interval"

# States
STATE_OK = "OK"
STATE_ERROR = "Error"
