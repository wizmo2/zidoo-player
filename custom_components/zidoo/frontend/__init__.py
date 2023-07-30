"""Zidoo Frontend"""
import logging
import os

from homeassistant.helpers.event import async_call_later

_LOGGER = logging.getLogger(__name__)

URL_BASE = "/zidoo"
ZIDOO_CARD_FILENAMES = ["zidoo-search-card.js"]

class ZidooCardRegistration:
    def __init__(self, hass):
        self.hass = hass

    async def async_register(self):
        await self.async_register_zidoo_path()
        if self.hass.data["lovelace"]["mode"] == "storage":
            await self.async_wait_for_lovelace_resources()

    # install card resources
    async def async_register_zidoo_path(self):
        # Register custom cards path
        self.hass.http.register_static_path(
            URL_BASE,
            self.hass.config.path("custom_components/zidoo/frontend"),
            cache_headers=False,
        )

    async def async_wait_for_lovelace_resources(self) -> None:
        async def check_lovelace_resources_loaded(now):
            if self.hass.data["lovelace"]["resources"].loaded:
                await self.async_register_zidoo_cards()
            else:
                _LOGGER.debug(
                    "Unable to install Zidoo card resources because Lovelace resources not yet loaded.  Trying again in 5 seconds."
                )
                async_call_later(self.hass, 5, check_lovelace_resources_loaded)

        await check_lovelace_resources_loaded(0)

    async def async_register_zidoo_cards(self):
        _LOGGER.debug("Installing Lovelace resources for zidoo cards")
        for card_filename in ZIDOO_CARD_FILENAMES:
            url = f"{URL_BASE}/{card_filename}"
            resource_loaded = [
                res["url"]
                for res in self.hass.data["lovelace"]["resources"].async_items()
                if res["url"] == url
            ]
            if not resource_loaded:
                resource_id = await self.hass.data["lovelace"][
                    "resources"
                ].async_create_item({"res_type": "module", "url": url})

    async def async_unregister(self):
        # Unload lovelace module resource
        if self.hass.data["lovelace"]["mode"] == "storage":
            for card_filename in ZIDOO_CARD_FILENAMES:
                url = f"{URL_BASE}/{card_filename}"
                zidoo_resources = [
                    resource
                    for resource in self.hass.data["lovelace"][
                        "resources"
                    ].async_items()
                    if resource["url"] == url
                ]
                for resource in zidoo_resources:
                    await self.hass.data["lovelace"]["resources"].async_delete_item(
                        resource.get("id")
                    )

