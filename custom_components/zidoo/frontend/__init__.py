"""Zidoo Frontend"""

import logging

from homeassistant.components.http import StaticPathConfig
from homeassistant.components.lovelace.const import LOVELACE_DATA
from homeassistant.helpers.event import async_call_later

_LOGGER = logging.getLogger(__name__)

URL_BASE = "/zidoo"
ZIDOO_CARD_FILENAMES = ["zidoo-search-card.js", "zidoo-remote-view.js"]


class ZidooCardRegistration:
    """Custom card registration."""

    def __init__(self, hass, domain):
        self.hass = hass
        self._version = getattr(hass.data["integrations"][domain], "version", "0")

    async def async_register(self):
        """Custom card registration."""
        await self.async_register_zidoo_path()
        await self.async_register_zidoo_cards()

    async def async_register_zidoo_path(self):
        """Install card resources."""
        # Register custom cards path
        await self.hass.http.async_register_static_paths(
            [
                StaticPathConfig(
                    URL_BASE,
                    self.hass.config.path("custom_components/zidoo/frontend"),
                    cache_headers=False,
                )
            ]
        )

    async def async_register_zidoo_cards(self):
        """Register cards."""
        resources = self.hass.data[LOVELACE_DATA].resources

        # Fix for 2026.x lazy-load issues #165773
        #  based on @renaudallard code.  Can be removes 2027.x
        if hasattr(resources, "loaded") and not resources.loaded:
            await resources.async_load()
            resources.loaded = True

        _LOGGER.debug("Installing Lovelace resources for zidoo cards")
        for card_filename in ZIDOO_CARD_FILENAMES:
            url = f"{URL_BASE}/{card_filename}"
            matched_resources = [
                resource
                for resource in resources.async_items()
                if resource["url"].startswith(url)
            ]
            url = f"{url}?v={self._version}"
            if not matched_resources:
                await resources.async_create_item({"res_type": "module", "url": url})
            else:
                for resource in matched_resources:
                    if resource.get("url") != url:
                        await resources.async_update_item(
                            resource["id"], {"res_type": "module", "url": url}
                        )

    async def async_unregister(self):
        """Unregister cards."""
        resources = self.hass.data[LOVELACE_DATA].resources

        # Unload lovelace module resource
        for card_filename in ZIDOO_CARD_FILENAMES:
            url = f"{URL_BASE}/{card_filename}"
            matched_resources = [
                resource
                for resource in resources.async_items()
                if resource["url"].startswith(url)
            ]
            for resource in matched_resources:
                await resources.async_delete_item(resource["id"])
