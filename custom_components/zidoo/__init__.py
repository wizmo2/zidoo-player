"""The Zidoo component."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_MAC, Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, _LOGGER
from .frontend import ZidooCardRegistration
from .zidooaio import ZidooRC
from .coordinator import ZidooCoordinator


PLATFORMS = [Platform.MEDIA_PLAYER, Platform.REMOTE]


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up zidoo from a config entry."""
    client = ZidooRC(
        config_entry.data[CONF_HOST], mac=config_entry.data.get(CONF_MAC, None)
    )
    coordinator = ZidooCoordinator(hass=hass, player=client, config_entry=config_entry)

    config_entry.async_on_unload(config_entry.add_update_listener(update_listener))
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    # Register custom cards
    cards = ZidooCardRegistration(hass)
    await cards.async_register()

    return True


async def async_unload_entry(hass: HomeAssistant, confid_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        confid_entry, PLATFORMS
    )
    if unload_ok:
        hass.data[DOMAIN].pop(confid_entry.entry_id)

    # Unload custom card resource if last instance
    confid_entry = [
        entry
        for entry in hass.config_entries.async_entries(DOMAIN)
        if not entry.disabled_by
    ]
    if len(confid_entry) == 0:
        cards = ZidooCardRegistration(hass)
        await cards.async_unregister()

    return unload_ok


async def update_listener(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)
