"""The Zidoo component."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, _LOGGER
from .frontend import ZidooCardRegistration

PLATFORMS = [Platform.MEDIA_PLAYER]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up zidoo from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register custom cards
    cards = ZidooCardRegistration(hass)
    await cards.async_register()

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    # Unload custom card resource if last instance
    entries = [
            entry
            for entry in hass.config_entries.async_entries(DOMAIN)
            if not entry.disabled_by
    ]
    if len(entries) == 0:
        cards = ZidooCardRegistration(hass)
        await cards.async_unregister()

    return unload_ok
