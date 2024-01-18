"""Update coordinator for Bravia TV integration."""
from __future__ import annotations

from datetime import timedelta
import logging
from types import MappingProxyType
from typing import Any, Final
from homeassistant.components.media_player import MediaPlayerState, MediaType
from homeassistant.core import HomeAssistant
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util.dt import utcnow

from .const import DOMAIN

from .zidooaio import (
    ZCONTENT_MUSIC,
    ZCONTENT_VIDEO,
    ZidooRC,
)

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL: Final = timedelta(seconds=5)
SCAN_INTERVAL_RAPID: Final = timedelta(seconds=1)


class ZidooCoordinator(DataUpdateCoordinator[None]):
    """Representation of a Zidoo Media Player Coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        player: ZidooRC,
        config_entry: MappingProxyType[str, Any],
    ) -> None:
        """Initialize the Zidoo device."""

        self._player = player
        self._config_entry = config_entry
        self._name = config_entry.title
        self._unique_id = config_entry.entry_id
        self._state = MediaPlayerState.OFF
        self._source = None
        self._source_list = None
        self._media_type = None
        self._media_info = {}
        self._last_update = None
        self._last_state = MediaPlayerState.OFF  # debug only

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
            request_refresh_debouncer=Debouncer(
                hass, _LOGGER, cooldown=1.0, immediate=False
            ),
        )

    async def async_refresh_channels(self, force=True):
        """Update source list."""
        if not force and not self._source_list:
            sources = await self.player.load_source_list()
            self._source_list = [ZCONTENT_VIDEO, ZCONTENT_MUSIC]
            for key in sources:
                self._source_list.append(key)

    async def _async_update_data(self) -> None:
        """Update data callback."""
        if not self.player.is_connected():
            if await self.player.get_power_status() != "off":
                await self.player.connect()

        # Retrieve the latest data.
        try:
            state = MediaPlayerState.OFF
            if self.player.is_connected():
                state = MediaPlayerState.PAUSED
                self._source = await self.player.get_source()
                playing_info = await self.player.get_playing_info()
                self._media_info = {}
                if playing_info is None or not playing_info:
                    self._media_type = MediaType.APP
                    state = MediaPlayerState.IDLE
                else:
                    self._media_info = playing_info
                    status = playing_info.get("status")
                    if status and status is not None:
                        if status == 1 or status is True:
                            state = MediaPlayerState.PLAYING
                    mediatype = playing_info.get("source")
                    if mediatype and mediatype is not None:
                        if mediatype == "video":
                            item_type = self._media_info.get("type")
                            if item_type is not None and item_type == "tv":
                                self._media_type = MediaType.TVSHOW
                            else:
                                self._media_type = MediaType.MOVIE
                            self._source = ZCONTENT_VIDEO
                        else:
                            self._media_type = MediaType.MUSIC
                            self._source = ZCONTENT_MUSIC
                    else:
                        self._media_type = MediaType.APP
                    self._last_update = utcnow()
                # Update source list
                await self.async_refresh_channels(force=False)
                # debug only
                if state != self._last_state:
                    _LOGGER.debug(
                        "%s New state (%s): %s", self._name, state, playing_info
                    )
                    self._last_state = state
            if state != self._last_state:
                _LOGGER.debug("%s New state (%s)", self._name, state)
                self._last_state = state

            self._state = state
            self.update_interval = (
                SCAN_INTERVAL if state == MediaPlayerState.OFF else SCAN_INTERVAL_RAPID
            )

        except Exception as exception_instance:  # pylint: disable=broad-except
            _LOGGER.error(exception_instance)

    @property
    def player(self):
        """Player Remote Control API Client."""
        return self._player

    @property
    def state(self):
        """State of device."""
        return self._state

    @property
    def media_type(self):
        """Type Current playing media."""
        return self._media_type

    @property
    def media_info(self):
        """Info of current playing media."""
        return self._media_info

    @property
    def source(self):
        """Current source."""
        return self._source

    @property
    def source_list(self):
        """Source List."""
        return self._source_list

    @property
    def last_updated(self):
        """Last state update."""
        return self._last_update
