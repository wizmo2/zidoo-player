"""Support for interface with Zidoo Media Player."""
from __future__ import annotations

import time
from typing import Iterable, Any

import voluptuous as vol

from homeassistant.components.remote import (
    ATTR_DELAY_SECS,
    ATTR_HOLD_SECS,
    ATTR_NUM_REPEATS,
    DEFAULT_DELAY_SECS,
    DEFAULT_HOLD_SECS,
    DEFAULT_NUM_REPEATS,
    RemoteEntity,
    RemoteEntityFeature
)
from homeassistant.components.media_player import (
    MediaPlayerState,
    MediaType,
)
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import (
    ATTR_ENTITY_ID,
    CONF_HOST,
    CONF_MAC,
    CONF_NAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util.dt import utcnow

from .const import (
    _LOGGER,
    AUDIO_SERVICE,
    BUTTON_SERVICE,
    CLIENTID_NICKNAME,
    CLIENTID_PREFIX,
    CONF_POWERMODE,
    DOMAIN,
    EVENT_TURN_ON,
    SUBTITLE_SERVICE,
)

from .zidoorc import (
    ZCONTENT_MUSIC,
    ZCONTENT_VIDEO,
    ZKEYS,
    ZidooRC,
)

DEFAULT_NAME = "Zidoo Remote"

ATTR_KEY = "key"



async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Add Media Player form configuration."""

    _LOGGER.warning(
        "Loading zidoo via platform config is deprecated, it will be automatically imported; Please remove it afterwards"
    )

    config_new = {
        CONF_NAME: config[CONF_NAME],
        CONF_HOST: config[CONF_HOST],
    }

    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_IMPORT}, data=config_new
        )
    )


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add Media Player from a config entry."""
    player = ZidooRC(
        config_entry.data[CONF_HOST], mac=config_entry.data.get(CONF_MAC, None)
    )

    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(SUBTITLE_SERVICE, {}, "async_set_subtitle")
    platform.async_register_entity_service(AUDIO_SERVICE, {}, "async_set_audio")
    platform.async_register_entity_service(
        BUTTON_SERVICE, {vol.Required(ATTR_KEY): vol.In(ZKEYS)}, "async_send_key"
    )

    entity = ZidooRemoteDevice(hass, player, config_entry)
    async_add_entities([entity])


class ZidooRemoteDevice(RemoteEntity):
    """Representation of a Zidoo Media."""

    _remote: ZidooRC

    def __init__(self, hass, remote, config_entry):
        """Initialize the Zidoo device."""

        self._remote = remote
        self._hass = hass
        self._name = config_entry.title
        self._unique_id = config_entry.entry_id
        self._state = MediaPlayerState.OFF
        self._muted = False
        self._source = None
        self._source_list = []
        self._content_mapping = {}
        self._playing = False
        self._media_type = None
        self._media_info = {}
        self._min_volume = None
        self._max_volume = None
        self._volume = None
        self._last_update = None
        self._config_entry = config_entry
        self._last_state = MediaPlayerState.OFF  # debug only

        # response = self._remote.connect(CLIENTID_PREFIX, CLIENTID_NICKNAME)
        # if response is not None:
        #    self.update()
        # else:
        #    self._state = STATE_OFF

    def update(self):
        """Update TV info."""
        if not self._remote.is_connected():
            if self._remote.get_power_status() != "off":
                self._remote.connect(CLIENTID_PREFIX, CLIENTID_NICKNAME)

        # Retrieve the latest data.
        try:
            state = MediaPlayerState.OFF
            if self._remote.is_connected():
                state = MediaPlayerState.PAUSED
                self._source = self._remote.get_source()
                playing_info = self._remote.get_playing_info()
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
                self._refresh_channels()
                # debug only
                if not state == self._last_state:
                    _LOGGER.debug("%s New state (%s): %s", self._name, state, playing_info)
                    self._last_state = state
            if not state == self._last_state:
                _LOGGER.debug("%s New state (%s)", self._name, state)
                self._last_state = state

            self._state = state

        except Exception as exception_instance:  # pylint: disable=broad-except
            _LOGGER.error(exception_instance)
    def _refresh_channels(self):
        if not self._source_list:
            self._content_mapping = self._remote.load_source_list()
            self._source_list = [ZCONTENT_VIDEO, ZCONTENT_MUSIC]
            for key in self._content_mapping:
                self._source_list.append(key)

    @property
    def unique_id(self):
        """Return the unique id of the device."""
        return self._unique_id

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for this device."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.unique_id)},
            manufacturer="Zidoo",
            name=self.name,
        )

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def current_activity(self):
        """Return the current activity."""
        return self._source

    @property
    def activity_list(self):
        """List of available activities."""
        return self._source_list

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return RemoteEntityFeature.LEARN_COMMAND | RemoteEntityFeature.ACTIVITY

    # def set_volume_level(self, volume):
    #    """Set volume level, range 0..1."""
    #    self._remote.set_volume_level(volume)

    async def async_turn_on(self):
        """Turn the media player on."""
        # Fire events for automations
        self.hass.bus.async_fire(EVENT_TURN_ON, {ATTR_ENTITY_ID: self.entity_id})
        # Try API and WOL
        self._remote.turn_on()

    async def async_turn_off(self):
        """Turn off media player."""
        await self.hass.async_add_executor_job(
            self._remote.turn_off, self._config_entry.options.get(CONF_POWERMODE, False)
        )

    def send_command(self, command: Iterable[str], **kwargs: Any) -> None:
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
                result = self._remote._send_key(single_command)
                _LOGGER.debug("send_command %s %d repeats %d delay : %r", ''.join(list(command)), num_repeats, delay_secs, result)
                time.sleep(delay_secs)
