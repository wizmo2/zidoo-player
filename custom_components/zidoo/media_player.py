"""Support for interface with Zidoo Media Player."""

from __future__ import annotations

import voluptuous as vol

from homeassistant.components import media_source
from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
)
from homeassistant.components.media_player.browse_media import (
    async_process_play_media_url,
)
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import ATTR_DEVICE_ID, ATTR_ENTITY_ID, CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    _LOGGER,
    AUDIO_SERVICE,
    BUTTON_SERVICE,
    DOMAIN,
    SUBTITLE_SERVICE,
    ZOOM_SERVICE,
)
from .coordinator import ZidooCoordinator
from .media_browser import (
    build_item_response,
    library_payload,
    media_source_content_filter,
)
from .zidooaio import ZKEYS, ZMUSIC_SEARCH_TYPES

ATTR_KEY = "key"

SUPPORT_ZIDOO = (
    MediaPlayerEntityFeature.VOLUME_STEP
    | MediaPlayerEntityFeature.VOLUME_MUTE
    | MediaPlayerEntityFeature.TURN_ON
    | MediaPlayerEntityFeature.TURN_OFF
    | MediaPlayerEntityFeature.SELECT_SOUND_MODE
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
    platform.async_register_entity_service(
        SUBTITLE_SERVICE,
        {vol.Optional("index"): cv.positive_int},
        "async_set_subtitle",
    )
    platform.async_register_entity_service(
        AUDIO_SERVICE,
        {vol.Optional("index"): cv.positive_int},
        "async_set_audio",
    )
    platform.async_register_entity_service(
        ZOOM_SERVICE, {vol.Optional("mode"): cv.string}, "async_set_zoom"
    )
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
    def sound_mode(self):
        """Return the current audio output source."""
        return self.coordinator.audio_output

    @property
    def sound_mode_list(self):
        """List of available audio outputs as sound modes."""
        return self.coordinator.audio_output_list

    @property
    def source(self):
        """Return the current input source."""
        return self.coordinator.source

    @property
    def source_list(self):
        """List of available input sources."""
        return self.coordinator.source_list

    @property
    def media_content_id(self) -> str | None:
        """Content ID of current playing media."""
        return self.coordinator.media_info.get("id")

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
        track = self.coordinator.media_info.get("track")
        return str(track).zfill(2) if track else None

    @property
    def media_series_title(self):
        """Return the title of the series of current playing media."""
        return self.coordinator.media_info.get("series_name")

    @property
    def media_season(self):
        """Season of current playing media (TV Show only)."""
        season = self.coordinator.media_info.get("season")
        return str(season).zfill(2) if season else None

    @property
    def media_episode(self):
        """Episode of current playing media (TV Show only)."""
        episode = self.coordinator.media_info.get("episode")
        return str(episode).zfill(2) if episode else None

    @property
    def media_duration(self):
        """Duration of current playing media in seconds."""
        duration = self.coordinator.media_info.get("duration")
        if duration:
            return float(duration) / 1000
        return None

    @property
    def media_position(self):
        """Position of current playing media in seconds."""
        position = self.coordinator.media_info.get("position")
        if position:
            return float(position) / 1000
        return None

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
            "channels",
            "imdb_id",
            "tmdb_id",
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
            return f"({date.year})"
        return ""

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

    async def async_select_sound_mode(self, sound_mode):
        """Set the audio output source."""
        await self.coordinator.async_set_audio_output(sound_mode)

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

    async def async_set_subtitle(self, index=None):
        """Sets or toggles the video subtitle."""
        await self.coordinator.player.set_subtitle(index)

    async def async_set_audio(self, index=None):
        """Sets or toggles the audio_track subtitle."""
        await self.coordinator.player.set_audio(index)

    async def async_set_zoom(self, mode=None):
        """Sets or toggles the audio_track subtitle."""
        await self.coordinator.player.set_zoom(mode)

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
            return await self._async_fetch_image(image_url)
        return (None, None)
