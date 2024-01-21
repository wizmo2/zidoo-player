"""Support for interface with Zidoo Media Player."""
from __future__ import annotations

from collections.abc import Iterable
import time
from typing import Any

from homeassistant.components.remote import (
    ATTR_DELAY_SECS,
    ATTR_HOLD_SECS,
    ATTR_NUM_REPEATS,
    DEFAULT_DELAY_SECS,
    DEFAULT_HOLD_SECS,
    DEFAULT_NUM_REPEATS,
    RemoteEntity,
    RemoteEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_ENTITY_ID,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    _LOGGER,
    CONF_POWERMODE,
    DOMAIN,
    EVENT_TURN_ON,
)
from .media_player import ZidooEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Zidoo Remote from a config entry."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    unique_id = config_entry.unique_id
    assert unique_id is not None

    async_add_entities([ZidooRemote(coordinator, config_entry)])


class ZidooRemote(ZidooEntity, RemoteEntity):
    """Representation of a Bravia TV Remote."""

    _attr_supported_features = (
        RemoteEntityFeature.LEARN_COMMAND | RemoteEntityFeature.ACTIVITY
    )

    @property
    def state(self):
        """Return the state of the device."""
        return self.coordinator.state

    @property
    def current_activity(self):
        """Return the current activity."""
        return self.coordinator.source

    @property
    def activity_list(self):
        """List of available activities."""
        return self.coordinator.source_list

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the media player on."""
        # Fire events for automations
        self.hass.bus.async_fire(EVENT_TURN_ON, {ATTR_ENTITY_ID: self.entity_id})
        # Try API and WOL
        await self.coordinator.player.turn_on()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off media player."""
        await self.coordinator.player.turn_off(
            self._config_entry.options.get(CONF_POWERMODE, False)
        )

    async def async_send_command(self, command: Iterable[str], **kwargs: Any) -> None:
        """Send commands to one device."""
        num_repeats = kwargs.get(ATTR_NUM_REPEATS, DEFAULT_NUM_REPEATS)
        delay_secs = kwargs.get(ATTR_DELAY_SECS, DEFAULT_DELAY_SECS)
        hold_secs = kwargs.get(ATTR_HOLD_SECS, DEFAULT_HOLD_SECS)

        for _ in range(num_repeats):
            for single_command in command:
                # Not supported : hold and release modes
                # if hold_secs > 0:
                #     self._device.send_key(single_command)
                #     time.sleep(hold_secs)
                # else:
                result = await self.coordinator.player._send_key(single_command)
                _LOGGER.debug(
                    "send_command %s %d repeats %d delay : %r",
                    "".join(list(command)),
                    num_repeats,
                    delay_secs,
                    result,
                )
                time.sleep(delay_secs)
