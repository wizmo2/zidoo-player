"""Diagnostics support for Zidoo."""

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_PIN, CONF_USERNAME
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import ZidooCoordinator

TO_REDACT = {CONF_USERNAME, CONF_PASSWORD, CONF_PIN}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: ZidooCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    device_info = await coordinator.player.get_system_info()

    return {
        "config_entry": async_redact_data(config_entry.as_dict(), TO_REDACT),
        "device_info": async_redact_data(device_info, TO_REDACT),
    }
