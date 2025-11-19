"""Constants for the Jokes integration."""

DOMAIN = "ha_jokes"
NAME = "Jokes"
VERSION = "1.3.1"

# API Configuration for icanhazdadjoke.com
API_URL_ICANHAZDADJOKE = "https://icanhazdadjoke.com"
API_HEADERS_ICANHAZDADJOKE = {
    "Accept": "application/json",
    "User-Agent": "Home Assistant Jokes Integration",
}

# API Configuration for JokeAPI v2
API_URL_JOKEAPI = "https://v2.jokeapi.dev/joke/Any?safe-mode&type=single"
API_HEADERS_JOKEAPI = {
    "Accept": "application/json",
    "User-Agent": "Home Assistant Jokes Integration",
}

# API Configuration for Official Joke API
API_URL_OFFICIAL = "https://official-joke-api.appspot.com/random_joke"
API_HEADERS_OFFICIAL = {
    "Accept": "application/json",
    "User-Agent": "Home Assistant Jokes Integration",
}

# Legacy API constants (for backward compatibility)
API_URL = API_URL_ICANHAZDADJOKE
API_HEADERS = API_HEADERS_ICANHAZDADJOKE

# Default Configuration
DEFAULT_REFRESH_INTERVAL = 5  # minutes
MIN_REFRESH_INTERVAL = 1     # minute
MAX_REFRESH_INTERVAL = 1440  # 24 hours in minutes

# Sensor Configuration
SENSOR_NAME = "Joke"
SENSOR_ICON = "mdi:emoticon-happy-outline"

# Configuration Keys
CONF_REFRESH_INTERVAL = "refresh_interval"
CONF_PROVIDERS = "providers"

# Attributes
ATTR_JOKE = "joke"
ATTR_JOKE_ID = "joke_id"
ATTR_LAST_UPDATED = "last_updated"
ATTR_REFRESH_INTERVAL = "refresh_interval"
ATTR_SOURCE = "source"
ATTR_EXPLANATION = "explanation"

# Provider names
PROVIDER_ICANHAZDADJOKE = "icanhazdadjoke"
PROVIDER_JOKEAPI = "jokeapi"
PROVIDER_OFFICIAL = "official_joke_api"

# Default providers (all enabled)
DEFAULT_PROVIDERS = [PROVIDER_ICANHAZDADJOKE, PROVIDER_JOKEAPI, PROVIDER_OFFICIAL]

# States
STATE_OK = "OK"
STATE_ERROR = "Error"
