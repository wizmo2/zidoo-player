"""Update coordinator for Zidoo Media Player integration."""

from __future__ import annotations

from datetime import timedelta
from typing import Any, Final

from homeassistant.components.media_player import MediaPlayerState, MediaType
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_UNIQUE_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util.dt import utcnow

from .const import _LOGGER, CONF_POWERMODE, DOMAIN, EVENT_TURN_ON
from .zidooaio import ZCONTENT_MUSIC, ZCONTENT_VIDEO, ZidooRC

SCAN_INTERVAL: Final = timedelta(seconds=5)
SCAN_INTERVAL_RAPID: Final = timedelta(seconds=1)


class ZidooCoordinator(DataUpdateCoordinator[None]):
    """Representation of a Zidoo Media Player Coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        player: ZidooRC,
        config_entry: ConfigEntry,
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
        self._last_state = MediaPlayerState.OFF

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
            await self.player.connect()

        # Retrieve the latest data.
        state = MediaPlayerState.OFF
        try:
            if self.player.is_connected():
                state = MediaPlayerState.PAUSED
                await self.async_refresh_channels(force=False)
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

        except Exception:  # noqa: BLE001
            return

        if state != self._last_state:
            _LOGGER.debug("%s New state (%s)", self._name, state)
            self._last_state = state
            self.update_interval = (
                SCAN_INTERVAL if state == MediaPlayerState.OFF else SCAN_INTERVAL_RAPID
            )
        self._state = state

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the media player on."""
        if self._state == MediaPlayerState.OFF:
            # Try 'zidoo.turn_on' event for automaton control
            data = kwargs.get("event_data", {CONF_UNIQUE_ID: self._unique_id})
            self.hass.bus.async_fire(EVENT_TURN_ON, data)
            # Try API and WOL
            await self._player.turn_on()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off media player."""
        if self._state != MediaPlayerState.OFF:
            await self._player.turn_off(
                self._config_entry.options.get(CONF_POWERMODE, False)
            )

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
