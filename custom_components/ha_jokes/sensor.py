"""Dad Jokes sensor platform."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
import logging
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
    API_HEADERS,
    API_URL,
    ATTR_JOKE,
    ATTR_JOKE_ID,
    ATTR_LAST_UPDATED,
    ATTR_REFRESH_INTERVAL,
    CONF_REFRESH_INTERVAL,
    DEFAULT_REFRESH_INTERVAL,
    DOMAIN,
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
    """Set up the Dad Jokes sensor platform."""
    refresh_interval = config_entry.options.get(
        CONF_REFRESH_INTERVAL, DEFAULT_REFRESH_INTERVAL
    )
    
    coordinator = DadJokesDataUpdateCoordinator(hass, refresh_interval)
    
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()
    
    async_add_entities([DadJokesSensor(coordinator, config_entry)], True)


class DadJokesDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching dad jokes data from the API."""

    def __init__(self, hass: HomeAssistant, refresh_interval: int) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=refresh_interval),
        )
        self.refresh_interval = refresh_interval

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API endpoint."""
        try:
            async with async_timeout.timeout(10):
                async with aiohttp.ClientSession() as session:
                    async with session.get(API_URL, headers=API_HEADERS) as response:
                        if response.status == 200:
                            data = await response.json()
                            return {
                                ATTR_JOKE: data.get("joke", ""),
                                ATTR_JOKE_ID: data.get("id", ""),
                                ATTR_LAST_UPDATED: datetime.now().isoformat(),
                                ATTR_REFRESH_INTERVAL: self.refresh_interval,
                            }
                        else:
                            raise UpdateFailed(f"Error fetching data: {response.status}")
        except asyncio.TimeoutError as err:
            raise UpdateFailed("Timeout communicating with API") from err
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err

    def update_refresh_interval(self, refresh_interval: int) -> None:
        """Update the refresh interval."""
        self.refresh_interval = refresh_interval
        self.update_interval = timedelta(minutes=refresh_interval)


class DadJokesSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Dad Jokes sensor."""

    def __init__(
        self,
        coordinator: DadJokesDataUpdateCoordinator,
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
        self.coordinator.update_refresh_interval(refresh_interval)
        await self.coordinator.async_request_refresh()