"""Support for interface with Zidoo Media Player."""
from __future__ import annotations

from enum import IntEnum
from typing import Iterable, Any

import voluptuous as vol

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
)

from homeassistant.components.media_player.browse_media import (
    async_process_play_media_url,
)
from homeassistant.components import media_source
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, ATTR_ENTITY_ID, ATTR_DEVICE_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    _LOGGER,
    AUDIO_SERVICE,
    BUTTON_SERVICE,
    DOMAIN,
    SUBTITLE_SERVICE,
)
from .media_browser import (
    build_item_response,
    library_payload,
    media_source_content_filter,
)
from .zidooaio import (
    ZKEYS,
    ZMUSIC_SEARCH_TYPES,
)
from .coordinator import ZidooCoordinator

ATTR_KEY = "key"

SUPPORT_ZIDOO = (
    MediaPlayerEntityFeature.VOLUME_STEP
    | MediaPlayerEntityFeature.VOLUME_MUTE
    | MediaPlayerEntityFeature.TURN_ON
    | MediaPlayerEntityFeature.TURN_OFF
    | MediaPlayerEntityFeature.SELECT_SOURCE
    | MediaPlayerEntityFeature.BROWSE_MEDIA
    | MediaPlayerEntityFeature.SEEK
)
# SUPPORT_CLEAR_PLAYLIST # SUPPORT_SELECT_SOUND_MODE # SUPPORT_SHUFFLE_SET # SUPPORT_VOLUME_SET

SUPPORT_MEDIA_MODES = (
    MediaPlayerEntityFeature.PAUSE
    | MediaPlayerEntityFeature.STOP
    | MediaPlayerEntityFeature.PREVIOUS_TRACK
    | MediaPlayerEntityFeature.NEXT_TRACK
    | MediaPlayerEntityFeature.PLAY
    | MediaPlayerEntityFeature.PLAY_MEDIA
)

class MediaPlayerEntityCommands(IntEnum):
    """List of available commands."""
    BACK = 1
    CURSOR_UP = 2
    CURSOR_DOWN = 3
    CURSOR_LEFT = 4
    CURSOR_RIGHT = 5
    CURSOR_ENTER = 6
    DIGIT_0 = 7
    DIGIT_1 = 8
    DIGIT_2 = 9
    DIGIT_3 = 10
    DIGIT_4 = 11
    DIGIT_5 = 12
    DIGIT_6 = 13
    DIGIT_7 = 14
    DIGIT_8 = 15
    DIGIT_9 = 16
    HOME = 17
    MENU = 18
    CONTEXT_MENU = 19
    INFO = 20

KEYMAP: dict[MediaPlayerEntityCommands, str] = {
    MediaPlayerEntityCommands.BACK : "Key.Back",
    MediaPlayerEntityCommands.CURSOR_UP : "Key.Up",
    MediaPlayerEntityCommands.CURSOR_DOWN : "Key.Down",
    MediaPlayerEntityCommands.CURSOR_LEFT : "Key.Left",
    MediaPlayerEntityCommands.CURSOR_RIGHT : "Key.Right",
    MediaPlayerEntityCommands.CURSOR_ENTER : "Key.Ok",
    MediaPlayerEntityCommands.DIGIT_0 : "Key.Number_0",
    MediaPlayerEntityCommands.DIGIT_1 : "Key.Number_1",
    MediaPlayerEntityCommands.DIGIT_2 : "Key.Number_2",
    MediaPlayerEntityCommands.DIGIT_3 : "Key.Number_3",
    MediaPlayerEntityCommands.DIGIT_4 : "Key.Number_4",
    MediaPlayerEntityCommands.DIGIT_5 : "Key.Number_5",
    MediaPlayerEntityCommands.DIGIT_6 : "Key.Number_6",
    MediaPlayerEntityCommands.DIGIT_7 : "Key.Number_7",
    MediaPlayerEntityCommands.DIGIT_8 : "Key.Number_8",
    MediaPlayerEntityCommands.DIGIT_9 : "Key.Number_9",
    MediaPlayerEntityCommands.HOME : "Key.Home",
    MediaPlayerEntityCommands.MENU : "Key.Menu",
    MediaPlayerEntityCommands.CONTEXT_MENU : "Key.PopMenu",
    MediaPlayerEntityCommands.INFO : "Key.Info"
}

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Add Media Player form configuration."""

    _LOGGER.warning(
        "Loading Zidoo via platform config is deprecated, it will be automatically imported; Please remove it afterwards"
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
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(SUBTITLE_SERVICE, {}, "async_set_subtitle")
    platform.async_register_entity_service(AUDIO_SERVICE, {}, "async_set_audio")
    platform.async_register_entity_service(
        BUTTON_SERVICE, {vol.Required(ATTR_KEY): vol.In(ZKEYS)}, "async_send_key"
    )

    async_add_entities([ZidooMediaPlayer(coordinator, config_entry)])


class ZidooEntity(CoordinatorEntity[ZidooCoordinator]):
    """Zidoo entity class."""

    def __init__(
        self,
        coordinator: ZidooCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)

        self._attr_unique_id = config_entry.entry_id
        self._attr_name = config_entry.title
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
            manufacturer="Zidoo",
            name=config_entry.title,
        )


class ZidooMediaPlayer(ZidooEntity, MediaPlayerEntity):
    """Zidoo Media Player."""

    _attr_supported_features = SUPPORT_ZIDOO | SUPPORT_MEDIA_MODES

    @property
    def state(self):
        """Return the state of the device."""
        return self.coordinator.state

    @property
    def source(self):
        """Return the current input source."""
        return self.coordinator.source

    @property
    def source_list(self):
        """List of available input sources."""
        return self.coordinator.source_list

    @property
    def media_content_type(self):
        """Content type of current playing media."""
        return self.coordinator.media_type

    # @property
    # def volume_level(self):
    #    """Volume level of the media player (0..1)."""
    #    if self._volume is not None:
    #        return self._volume / 100
    #    return None

    @property
    def media_title(self):
        """Title of current playing media."""
        media_info = self.coordinator.media_info
        title = media_info.get("movie_name")
        if title is None:
            title = media_info.get("episode_name")
        if title is not None:
            return title
        return media_info.get("title")

    @property
    def media_artist(self):
        """Artist of current playing media."""
        return self.coordinator.media_info.get("artist")

    @property
    def media_album_name(self):
        """Album of current playing media."""
        return self.coordinator.media_info.get("album")

    @property
    def media_track(self):
        """Track number of current playing media (Music track only)."""
        return self.coordinator.media_info.get("track")

    @property
    def media_series_title(self):
        """Return the title of the series of current playing media."""
        return self.coordinator.media_info.get("series_name")

    @property
    def media_season(self):
        """Season of current playing media (TV Show only)."""
        return str(self.coordinator.media_info.get("season")).zfill(2)

    @property
    def media_episode(self):
        """Episode of current playing media (TV Show only)."""
        return str(self.coordinator.media_info.get("episode")).zfill(2)

    @property
    def media_duration(self):
        """Duration of current playing media in seconds."""
        duration = self.coordinator.media_info.get("duration")
        if duration:
            return float(duration) / 1000

    @property
    def media_position(self):
        """Position of current playing media in seconds."""
        position = self.coordinator.media_info.get("position")
        if position:
            return float(position) / 1000

    @property
    def media_position_updated_at(self):
        """Last time status was updated."""
        return self.coordinator.last_updated

    @property
    def extra_state_attributes(self):
        """Return the device specific state attributes."""
        extras = {
            "uri",
            "height",
            "width",
            "zoom",
            "tag",
            "date",
            "bitrate",
            "fps",
            "audio",
            "video",
        }
        attributes = {}
        for item in extras:
            value = self.coordinator.media_info.get(item)
            if value:
                attributes["media_" + item] = value

        return attributes

    @property
    def app_name(self):
        """Return the current running application."""
        date = self.coordinator.media_info.get("date")
        if self.coordinator.media_type == MediaType.MOVIE and date is not None:
            return "({})".format(date.year)

    # def set_volume_level(self, volume):
    #    """Set volume level, range 0..1."""
    #    self.coordinator.player.set_volume_level(volume)

    async def async_turn_on(self):
        """Turn the media player on."""
        await self.coordinator.async_turn_on(
            event_data={
                ATTR_ENTITY_ID: self.entity_id,
                ATTR_DEVICE_ID: self.device_entry.id,
            }
        )

    async def async_turn_off(self):
        """Turn off media player."""
        await self.coordinator.async_turn_off()

    async def async_volume_up(self):
        """Volume up the media player."""
        await self.coordinator.player.volume_up()

    async def async_volume_down(self):
        """Volume down media player."""
        await self.coordinator.player.volume_down()

    async def async_mute_volume(self, mute):
        """Send mute command."""
        await self.coordinator.player.mute_volume()

    async def async_select_source(self, source):
        """Set the input source."""
        await self.coordinator.player.start_app(source)

    async def async_media_play_pause(self):
        """Simulate play pause media player."""
        if self.state == MediaPlayerState.PLAYING:
            return await self.async_media_pause()
        return await self.async_media_play()

    async def async_media_play(self):
        """Send play command."""
        return await self.coordinator.player.media_play()

    async def async_media_pause(self):
        """Send media pause command."""
        return await self.coordinator.player.media_pause()

    async def async_media_stop(self):
        """Send media stop command."""
        return await self.coordinator.player.media_stop()

    async def async_media_next_track(self):
        """Send next track command."""
        return await self.coordinator.player.media_next_track()
        # self.schedule_update_ha_state()

    async def async_media_previous_track(self):
        """Send the previous track command."""
        return await self.coordinator.player.media_previous_track()
        # self.schedule_update_ha_state()

    async def async_play_media(self, media_type, media_id, **kwargs):
        """Play a piece of media."""
        _LOGGER.debug("play request: media_id:%s media_type:%s", media_id, media_type)
        if media_source.is_media_source_id(media_id):
            play_item = await media_source.async_resolve_media(
                self.hass, media_id, self.entity_id
            )
            media_id = async_process_play_media_url(self.hass, play_item.url)
            media_type = play_item.mime_type

        _LOGGER.debug("play: media_id:%s media_type:%s", media_id, media_type)
        if media_type and media_type == "file":
            await self.coordinator.player.play_file(media_id)
        elif media_type in ZMUSIC_SEARCH_TYPES:
            media_ids = media_id.split(",")
            await self.coordinator.player.play_music(
                media_ids[0], media_type, media_ids[-1]
            )
        elif "/" in media_type:
            await self.coordinator.player.play_stream(media_id, media_type)
        else:
            await self.coordinator.player.play_movie(media_id)

    async def async_media_seek(self, position):
        """Send media_seek command to media player."""
        await self.coordinator.player.set_media_position(float(position) * 1000)

    @property
    def media_image_url(self):
        """Image url of current playing media."""
        return self.coordinator.player.generate_current_image_url()

    async def async_set_subtitle(self):
        """Sets or toggles the video subtitle."""
        await self.coordinator.player.set_subtitle()

    async def async_set_audio(self):
        """Sets or toggles the audio_track subtitle."""
        await self.coordinator.player.set_audio()

    async def async_send_command(self, command: Iterable[str], **kwargs: Any) -> None:
        for cmd in command:
            try:
                keymap = KEYMAP.get(MediaPlayerEntityCommands(cmd), None)
                if keymap is None:
                    await self.coordinator.player._send_key(cmd)
                else:
                    await self.coordinator.player._send_key(keymap)
            except Exception:
                await self.coordinator.player._send_key(cmd)

    async def async_send_key(self, key):
        """Send a remote control key command."""
        _LOGGER.warning(
            "'Zidoo:Send Keys' is depreciated.  Please update to use 'Remote:Send command'"
        )
        await self.coordinator.player._send_key(key)

    async def async_browse_media(self, media_content_type=None, media_content_id=None):
        """Implement the websocket media browsing helper."""
        if media_content_type in [None, "library"]:
            return await library_payload(self)

        if media_source.is_media_source_id(media_content_id):
            return await media_source.async_browse_media(
                self.hass, media_content_id, content_filter=media_source_content_filter
            )

        payload = {
            "search_type": media_content_type,
            "search_id": media_content_id,
        }

        return await build_item_response(self, payload)

    async def async_get_browse_image(
        self, media_content_type, media_content_id, media_image_id=None
    ):
        """Get media image from server."""
        image_url = self.coordinator.player.generate_image_url(
            media_content_id, media_content_type
        )
        if image_url:
            result = await self._async_fetch_image(image_url)
            return result

        return (None, None)
