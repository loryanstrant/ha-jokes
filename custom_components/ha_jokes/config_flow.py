"""Config flow for Dad Jokes integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_REFRESH_INTERVAL,
    DEFAULT_REFRESH_INTERVAL,
    DOMAIN,
    MAX_REFRESH_INTERVAL,
    MIN_REFRESH_INTERVAL,
    NAME,
)

_LOGGER = logging.getLogger(__name__)


class DadJokesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Dad Jokes."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate refresh interval
            refresh_interval = user_input[CONF_REFRESH_INTERVAL]
            if not (MIN_REFRESH_INTERVAL <= refresh_interval <= MAX_REFRESH_INTERVAL):
                errors[CONF_REFRESH_INTERVAL] = "invalid_refresh_interval"
            else:
                # Create the config entry
                return self.async_create_entry(
                    title=NAME,
                    data={},
                    options={CONF_REFRESH_INTERVAL: refresh_interval},
                )

        # Schema for the configuration form
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_REFRESH_INTERVAL, default=DEFAULT_REFRESH_INTERVAL
                ): vol.All(cv.positive_int, vol.Range(min=MIN_REFRESH_INTERVAL, max=MAX_REFRESH_INTERVAL)),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> DadJokesOptionsFlow:
        """Get the options flow for this handler."""
        return DadJokesOptionsFlow(config_entry)


class DadJokesOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Dad Jokes."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate refresh interval
            refresh_interval = user_input[CONF_REFRESH_INTERVAL]
            if not (MIN_REFRESH_INTERVAL <= refresh_interval <= MAX_REFRESH_INTERVAL):
                errors[CONF_REFRESH_INTERVAL] = "invalid_refresh_interval"
            else:
                return self.async_create_entry(title="", data=user_input)

        # Get current options or defaults
        current_refresh_interval = self.config_entry.options.get(
            CONF_REFRESH_INTERVAL, DEFAULT_REFRESH_INTERVAL
        )

        # Schema for the options form
        options_schema = vol.Schema(
            {
                vol.Required(
                    CONF_REFRESH_INTERVAL, default=current_refresh_interval
                ): vol.All(cv.positive_int, vol.Range(min=MIN_REFRESH_INTERVAL, max=MAX_REFRESH_INTERVAL)),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            errors=errors,
        )