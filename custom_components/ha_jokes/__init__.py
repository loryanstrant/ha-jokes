"""The Jokes integration."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    DOMAIN,
    CONF_REFRESH_INTERVAL,
    CONF_PROVIDERS,
    DEFAULT_REFRESH_INTERVAL,
    DEFAULT_PROVIDERS,
    VERSION,
)
from .sensor import JokesDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

# URL the bundled Lovelace card is served from, and the flag key used to ensure
# the frontend resource is only registered once per Home Assistant instance.
CARD_URL = f"/{DOMAIN}_frontend/ha-jokes-card.js"
FRONTEND_REGISTERED = f"{DOMAIN}_frontend_registered"


async def _async_register_frontend(hass: HomeAssistant) -> None:
    """Serve and auto-load the bundled custom Lovelace card (idempotent)."""
    if hass.data.get(FRONTEND_REGISTERED):
        return

    card_path = Path(__file__).parent / "www" / "ha-jokes-card.js"

    try:
        from homeassistant.components.http import StaticPathConfig

        await hass.http.async_register_static_paths(
            [StaticPathConfig(CARD_URL, str(card_path), False)]
        )
    except ImportError:
        # Older cores: fall back to the (deprecated) sync registration.
        hass.http.register_static_path(CARD_URL, str(card_path), False)

    try:
        from homeassistant.components.frontend import add_extra_js_url

        # ?v= busts the browser module cache when the integration is upgraded.
        add_extra_js_url(hass, f"{CARD_URL}?v={VERSION}")
    except ImportError:
        _LOGGER.warning(
            "Could not auto-load ha-jokes-card; add %s as a Lovelace resource manually",
            CARD_URL,
        )

    hass.data[FRONTEND_REGISTERED] = True
    _LOGGER.debug("Registered ha-jokes-card frontend resource at %s", CARD_URL)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Jokes from a config entry."""
    _LOGGER.debug("Setting up Jokes integration")

    # Store the config entry data in hass.data
    hass.data.setdefault(DOMAIN, {})

    # Serve and auto-load the bundled custom Lovelace card (once per instance)
    await _async_register_frontend(hass)
    
    # Get refresh interval and providers from options
    refresh_interval = entry.options.get(
        CONF_REFRESH_INTERVAL, DEFAULT_REFRESH_INTERVAL
    )
    enabled_providers = entry.options.get(
        CONF_PROVIDERS, DEFAULT_PROVIDERS
    )
    
    # Create coordinator
    coordinator = JokesDataUpdateCoordinator(hass, refresh_interval, enabled_providers)
    
    # Fetch initial data - this can raise ConfigEntryNotReady
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.error("Jokes integration failed to fetch initial data: %s", err)
        raise ConfigEntryNotReady from err
    
    # Store coordinator in hass.data
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "data": entry.data,
        "explanation_entity": None,  # Will be set by the sensor platform
    }
    
    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Register the explain_joke action (only once)
    async def handle_explain_joke(call):
        """Handle the explain_joke action."""
        # Find the explanation sensor entity for any entry
        explanation_entity = None
        for entry_id, entry_data in hass.data[DOMAIN].items():
            if isinstance(entry_data, dict) and "explanation_entity" in entry_data:
                explanation_entity = entry_data["explanation_entity"]
                if explanation_entity:
                    break
        
        if not explanation_entity:
            _LOGGER.error("Joke Explanation entity not found or not yet initialized")
            return
        
        await explanation_entity.async_explain_joke()
    
    # Only register the service if it hasn't been registered yet
    if not hass.services.has_service(DOMAIN, "explain_joke"):
        hass.services.async_register(DOMAIN, "explain_joke", handle_explain_joke)
    
    # Set up options update listener
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading Jokes integration")
    
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        
        # Unregister service if no more entries
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, "explain_joke")
    
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
