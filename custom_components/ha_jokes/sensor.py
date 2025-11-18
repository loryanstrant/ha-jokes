"""Jokes sensor platform."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
import logging
import random
from typing import Any

import aiohttp
import async_timeout

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    API_HEADERS_ICANHAZDADJOKE,
    API_HEADERS_JOKEAPI,
    API_HEADERS_OFFICIAL,
    API_URL_ICANHAZDADJOKE,
    API_URL_JOKEAPI,
    API_URL_OFFICIAL,
    ATTR_EXPLANATION,
    ATTR_JOKE,
    ATTR_JOKE_ID,
    ATTR_LAST_UPDATED,
    ATTR_REFRESH_INTERVAL,
    ATTR_SOURCE,
    CONF_PROVIDERS,
    CONF_REFRESH_INTERVAL,
    DEFAULT_PROVIDERS,
    DEFAULT_REFRESH_INTERVAL,
    DOMAIN,
    PROVIDER_ICANHAZDADJOKE,
    PROVIDER_JOKEAPI,
    PROVIDER_OFFICIAL,
    SENSOR_ICON,
    SENSOR_NAME,
    STATE_ERROR,
    STATE_OK,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Jokes sensor platform."""
    # Get coordinator from hass.data
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    
    # Create main joke sensor and explanation sensor
    async_add_entities([
        JokesSensor(coordinator, config_entry),
        JokeExplanationSensor(coordinator, config_entry),
    ], True)


class JokesDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def _build_provider_configs(self) -> list[dict[str, Any]]:
        """Build provider configurations."""
        return [
            {
                "name": PROVIDER_ICANHAZDADJOKE,
                "url": API_URL_ICANHAZDADJOKE,
                "headers": API_HEADERS_ICANHAZDADJOKE,
                "parser": self._parse_icanhazdadjoke,
            },
            {
                "name": PROVIDER_JOKEAPI,
                "url": API_URL_JOKEAPI,
                "headers": API_HEADERS_JOKEAPI,
                "parser": self._parse_jokeapi,
            },
            {
                "name": PROVIDER_OFFICIAL,
                "url": API_URL_OFFICIAL,
                "headers": API_HEADERS_OFFICIAL,
                "parser": self._parse_official_joke_api,
            },
        ]

    def __init__(self, hass: HomeAssistant, refresh_interval: int, enabled_providers: list[str]) -> None:
        """Initialize."""
        self.platforms = []
        self._refresh_interval = refresh_interval
        self._enabled_providers = enabled_providers if enabled_providers else DEFAULT_PROVIDERS
        
        # Filter to only enabled providers
        self._providers = [p for p in self._build_provider_configs() if p["name"] in self._enabled_providers]
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=refresh_interval),
        )

    def _parse_icanhazdadjoke(self, data: dict) -> dict[str, Any]:
        """Parse icanhazdadjoke.com response."""
        return {
            ATTR_JOKE: data.get("joke", ""),
            ATTR_JOKE_ID: data.get("id", ""),
            ATTR_SOURCE: "icanhazdadjoke.com",
        }

    def _parse_jokeapi(self, data: dict) -> dict[str, Any]:
        """Parse JokeAPI v2 response."""
        # JokeAPI returns different formats for single and two-part jokes
        # We're using type=single, so we get the 'joke' field
        joke_text = data.get("joke", "")
        joke_id = str(data.get("id", ""))
        
        return {
            ATTR_JOKE: joke_text,
            ATTR_JOKE_ID: joke_id,
            ATTR_SOURCE: "jokeapi.dev",
        }

    def _parse_official_joke_api(self, data: dict) -> dict[str, Any]:
        """Parse Official Joke API response."""
        # Official Joke API returns setup and punchline separately
        setup = data.get("setup", "")
        punchline = data.get("punchline", "")
        joke_text = f"{setup} {punchline}" if setup and punchline else ""
        joke_id = str(data.get("id", ""))
        
        return {
            ATTR_JOKE: joke_text,
            ATTR_JOKE_ID: joke_id,
            ATTR_SOURCE: "official-joke-api.appspot.com",
        }

    async def _fetch_from_provider(
        self, session: aiohttp.ClientSession, provider: dict
    ) -> dict[str, Any] | None:
        """Fetch joke from a specific provider."""
        try:
            async with session.get(
                provider["url"], headers=provider["headers"]
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    parsed = provider["parser"](data)
                    _LOGGER.debug(
                        "Successfully fetched joke from %s", provider["name"]
                    )
                    return parsed
                else:
                    _LOGGER.warning(
                        "Provider %s returned status %s",
                        provider["name"],
                        response.status,
                    )
                    return None
        except Exception as err:
            _LOGGER.warning(
                "Error fetching from provider %s: %s", provider["name"], err
            )
            return None

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library with fault tolerance."""
        # Randomize provider order for each request
        providers = self._providers.copy()
        random.shuffle(providers)
        
        _LOGGER.debug("Attempting to fetch joke from providers in random order")
        
        try:
            async with async_timeout.timeout(30):
                async with aiohttp.ClientSession() as session:
                    # Try each provider until one succeeds
                    for provider in providers:
                        result = await self._fetch_from_provider(session, provider)
                        if result:
                            # Add common attributes
                            result[ATTR_LAST_UPDATED] = datetime.now().isoformat()
                            result[ATTR_REFRESH_INTERVAL] = self._refresh_interval
                            return result
                    
                    # If all providers failed
                    raise UpdateFailed("All joke providers failed to respond")
                    
        except asyncio.TimeoutError as exception:
            raise UpdateFailed(
                f"Timeout communicating with joke APIs: {exception}"
            ) from exception
        except UpdateFailed:
            raise
        except Exception as exception:
            raise UpdateFailed(
                f"Error communicating with joke APIs: {exception}"
            ) from exception

    def update_refresh_interval(self, refresh_interval: int) -> None:
        """Update the refresh interval."""
        self._refresh_interval = refresh_interval
        self.update_interval = timedelta(minutes=refresh_interval)

    def update_enabled_providers(self, enabled_providers: list[str]) -> None:
        """Update the enabled providers."""
        self._enabled_providers = enabled_providers if enabled_providers else DEFAULT_PROVIDERS
        
        # Rebuild providers list using centralized configuration
        self._providers = [p for p in self._build_provider_configs() if p["name"] in self._enabled_providers]


class JokesSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Jokes sensor."""

    def __init__(
        self,
        coordinator: JokesDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_name = SENSOR_NAME
        self._attr_icon = SENSOR_ICON
        self._attr_unique_id = f"{DOMAIN}_{config_entry.entry_id}"

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        if self.coordinator.last_update_success:
            return STATE_OK
        return STATE_ERROR

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if not self.coordinator.data:
            return {}
        
        return {
            ATTR_JOKE: self.coordinator.data.get(ATTR_JOKE, ""),
            ATTR_JOKE_ID: self.coordinator.data.get(ATTR_JOKE_ID, ""),
            ATTR_SOURCE: self.coordinator.data.get(ATTR_SOURCE, ""),
            ATTR_LAST_UPDATED: self.coordinator.data.get(ATTR_LAST_UPDATED, ""),
            ATTR_REFRESH_INTERVAL: self.coordinator.data.get(ATTR_REFRESH_INTERVAL, DEFAULT_REFRESH_INTERVAL),
        }

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        
        # Listen for options updates
        self._config_entry.async_on_unload(
            self._config_entry.add_update_listener(self._async_update_options)
        )

    async def _async_update_options(self, config_entry: ConfigEntry) -> None:
        """Update options."""
        refresh_interval = config_entry.options.get(
            CONF_REFRESH_INTERVAL, DEFAULT_REFRESH_INTERVAL
        )
        enabled_providers = config_entry.options.get(
            CONF_PROVIDERS, DEFAULT_PROVIDERS
        )
        self.coordinator.update_refresh_interval(refresh_interval)
        self.coordinator.update_enabled_providers(enabled_providers)
        await self.coordinator.async_request_refresh()


class JokeExplanationSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Joke Explanation sensor."""

    def __init__(
        self,
        coordinator: JokesDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_name = "Joke Explanation"
        self._attr_icon = "mdi:comment-question-outline"
        self._attr_unique_id = f"{DOMAIN}_{config_entry.entry_id}_explanation"
        self._explanation = None

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        if self._explanation:
            return "Explained"
        return "Not Explained"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return {
            ATTR_EXPLANATION: self._explanation or "No explanation available",
        }

    async def async_explain_joke(self) -> None:
        """Explain the current joke using AI."""
        # Find the joke sensor entity dynamically
        joke = None
        joke_entity_id = None
        
        # Search for the joke sensor entity
        for entity_id in self.hass.states.async_entity_ids("sensor"):
            if entity_id.startswith(f"sensor.{DOMAIN}_") and "explanation" not in entity_id:
                # This is likely our joke sensor
                state = self.hass.states.get(entity_id)
                if state and state.attributes.get(ATTR_JOKE):
                    joke = state.attributes.get(ATTR_JOKE)
                    joke_entity_id = entity_id
                    break
            elif entity_id == "sensor.joke":
                # Check for the main joke sensor by name
                state = self.hass.states.get(entity_id)
                if state and state.attributes.get(ATTR_JOKE):
                    joke = state.attributes.get(ATTR_JOKE)
                    joke_entity_id = entity_id
                    break
        
        if not joke:
            _LOGGER.warning("No joke available to explain")
            self._explanation = "No joke available to explain"
            self.async_write_ha_state()
            return
        
        # Check if ai_task service is available
        if not self.hass.services.has_service("ai_task", "generate_data"):
            _LOGGER.error("ai_task.generate_data service is not available. Please configure an AI provider.")
            self._explanation = "AI service not configured. Please configure an AI provider in Home Assistant."
            self.async_write_ha_state()
            return
        
        try:
            # Call the ai_task.generate_data service with correct parameters
            _LOGGER.debug("Calling ai_task.generate_data for joke from %s", joke_entity_id)
            response = await self.hass.services.async_call(
                "ai_task",
                "generate_data",
                {
                    "task_name": "explain_joke",
                    "instructions": f"Explain the following joke in plain language:\n{joke}",
                },
                blocking=True,
                return_response=True,
            )
            
            if response:
                self._explanation = response.get("text", "Unable to generate explanation")
            else:
                self._explanation = "No response from AI service"
                
            self.async_write_ha_state()
            _LOGGER.debug("Joke explanation generated successfully")
            
        except Exception as err:
            _LOGGER.error("Failed to generate joke explanation: %s", err)
            self._explanation = f"Error: {str(err)}"
            self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        
        # Store reference to this entity in hass.data for service calls
        if DOMAIN in self.hass.data and self._config_entry.entry_id in self.hass.data[DOMAIN]:
            self.hass.data[DOMAIN][self._config_entry.entry_id]["explanation_entity"] = self
