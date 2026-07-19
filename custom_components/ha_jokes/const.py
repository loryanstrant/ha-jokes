"""Constants for the Jokes integration."""

DOMAIN = "ha_jokes"
NAME = "Jokes"
VERSION = "1.4.0"

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

# API Configuration for Geek Jokes (unfiltered — largely Chuck Norris + crude material;
# not family-friendly, so it is opt-in rather than a default provider)
API_URL_GEEKJOKES = "https://geek-jokes.sameerkumar.website/api?format=json"
API_HEADERS_GEEKJOKES = {
    "Accept": "application/json",
    "User-Agent": "Home Assistant Jokes Integration",
}

# API Configuration for Yo Mama Jokes (adult/roast humour — not family-friendly)
API_URL_YOMAMA = "https://www.yomama-jokes.com/api/v1/jokes/random/"
API_HEADERS_YOMAMA = {
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
PROVIDER_GEEKJOKES = "geek_jokes"
PROVIDER_YOMAMA = "yomama_jokes"

# Default providers (family-friendly sources enabled by default).
# PROVIDER_GEEKJOKES and PROVIDER_YOMAMA are intentionally excluded — both serve
# unfiltered adult/edgy content (Geek Jokes is largely Chuck Norris + crude material;
# Yo Mama is roast humour) and must be opted into explicitly.
DEFAULT_PROVIDERS = [
    PROVIDER_ICANHAZDADJOKE,
    PROVIDER_JOKEAPI,
    PROVIDER_OFFICIAL,
]

# States
STATE_OK = "OK"
STATE_ERROR = "Error"
