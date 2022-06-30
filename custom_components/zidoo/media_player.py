"""Support for interface with Zidoo Media Player."""
from __future__ import annotations

from .zidoorc import ZidooRC, ZCONTENT_MUSIC, ZCONTENT_VIDEO, ZMUSIC_SEARCH_TYPES, ZTYPE_MIMETYPE
import voluptuous as vol

from homeassistant.components.media_player import MediaPlayerEntity, BrowseMedia, MediaPlayerEntityFeature
from homeassistant.components.media_player.const import (
    MEDIA_TYPE_MUSIC,
    MEDIA_TYPE_TVSHOW,
    MEDIA_TYPE_MOVIE,
    MEDIA_TYPE_APP,
)
from homeassistant.components.media_player.browse_media import async_process_play_media_url
from homeassistant.components import media_source
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.network import is_internal_request
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util.dt import utcnow

from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_MAC,
    STATE_IDLE,
    STATE_OFF,
    STATE_PAUSED,
    STATE_PLAYING,
    ATTR_ENTITY_ID,
)
from .const import (
    DOMAIN,
    _LOGGER,
    CLIENTID_PREFIX,
    CLIENTID_NICKNAME,
    CONF_POWERMODE,
    SUBTITLE_SERVICE,
    AUDIO_SERVICE,
    SEARCH_SERVICE,
    EVENT_TURN_ON,
)

from .media_browser import browse_media  # build_item_response, library_payload

DEFAULT_NAME = "Zidoo Media Player"

QUERY_STRING = "query_string"
VIDEO_TYPE = "search_type"

SEARCH_SCHEMA = {vol.Optional(QUERY_STRING): str, vol.Optional(VIDEO_TYPE): str}

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
    platform.async_register_entity_service(
        SEARCH_SERVICE, SEARCH_SCHEMA, "async_search_media"
    )
    platform.async_register_entity_service(SUBTITLE_SERVICE, {}, "async_set_subtitle")
    platform.async_register_entity_service(AUDIO_SERVICE, {}, "async_set_audio")

    entity = ZidooPlayerDevice(hass, player, config_entry)
    async_add_entities([entity])

class ZidooPlayerDevice(MediaPlayerEntity):
    """Representation of a Zidoo Media."""

    def __init__(self, hass, player, config_entry):
        """Initialize the Zidoo device."""

        self._player = player
        self._hass = hass
        self._name = config_entry.title
        self._unique_id = config_entry.entry_id
        self._state = STATE_OFF
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
        self._search_query = None
        self._search_type = None
        self._config_entry = config_entry

        # response = self._player.connect(CLIENTID_PREFIX, CLIENTID_NICKNAME)
        # if response is not None:
        #    self.update()
        # else:
        #    self._state = STATE_OFF

    def update(self):
        """Update TV info."""
        if not self._player.is_connected():
            if self._player.get_power_status() != "off":
                self._player.connect(CLIENTID_PREFIX, CLIENTID_NICKNAME)
            if not self._player.is_connected():
                return

        # Retrieve the latest data.
        try:
            power_status = self._player.get_power_status()
            if power_status == "on":
                self._state = STATE_PAUSED
                self._source = self._player.get_source()
                playing_info = self._player.get_playing_info()
                self._media_info = {}
                if playing_info is None or not playing_info:
                    self._media_type = MEDIA_TYPE_APP
                    self._state = STATE_IDLE
                else:
                    self._media_info = playing_info
                    status = playing_info.get("status")
                    if status and status is not None:
                        if status == 1 or status is True:
                            self._state = STATE_PLAYING
                    mediatype = playing_info.get("source")
                    if mediatype and mediatype is not None:
                        if mediatype == "video":
                            item_type = self._media_info.get("type")
                            if item_type is not None and item_type == "tv":
                                self._media_type = MEDIA_TYPE_TVSHOW
                            else:
                                self._media_type = MEDIA_TYPE_MOVIE
                            self._source = ZCONTENT_VIDEO
                        else:
                            self._media_type = MEDIA_TYPE_MUSIC
                            self._source = ZCONTENT_MUSIC
                    else:
                        self._media_type = MEDIA_TYPE_APP
                    self._last_update = utcnow()
                self._refresh_channels()
            else:
                self._state = STATE_OFF

        except Exception as exception_instance:  # pylint: disable=broad-except
            _LOGGER.error(exception_instance)
            # self._state = STATE_OFF

    def _refresh_volume(self):
        """Refresh volume information."""
        volume_info = self._player.get_volume_info()
        if volume_info is not None:
            self._volume = volume_info.get("volume")
            self._min_volume = volume_info.get("minVolume")
            self._max_volume = volume_info.get("maxVolume")
            self._muted = volume_info.get("mute")

    def _refresh_channels(self):
        if not self._source_list:
            self._content_mapping = self._player.load_source_list()
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
    def source(self):
        """Return the current input source."""
        return self._source

    @property
    def source_list(self):
        """List of available input sources."""
        return self._source_list

    @property
    def media_content_type(self):
        """Content type of current playing media."""
        return self._media_type

    # @property
    # def volume_level(self):
    #    """Volume level of the media player (0..1)."""
    #    if self._volume is not None:
    #        return self._volume / 100
    #    return None

    @property
    def is_volume_muted(self):
        """Boolean if volume is currently muted."""
        return self._muted

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_ZIDOO | SUPPORT_MEDIA_MODES

    @property
    def media_title(self):
        """Title of current playing media."""
        title = self._media_info.get("movie_name")
        if title is None:
            title = self._media_info.get("episode_name")
        if title is not None:
            return title
        return self._media_info.get("title")

    @property
    def media_artist(self):
        """Artist of current playing media."""
        return self._media_info.get("artist")

    @property
    def media_album_name(self):
        """Album of current playing media."""
        return self._media_info.get("album")

    @property
    def media_track(self):
        """Track number of current playing media (Music track only)."""
        return self._media_info.get("track")

    @property
    def media_series_title(self):
        """Return the title of the series of current playing media."""
        return self._media_info.get("series_name")

    @property
    def media_season(self):
        """Season of current playing media (TV Show only)."""
        return str(self._media_info.get("season")).zfill(2)

    @property
    def media_episode(self):
        """Episode of current playing media (TV Show only)."""
        return str(self._media_info.get("episode")).zfill(2)

    @property
    def media_duration(self):
        """Duration of current playing media in seconds."""
        return self._media_info.get("duration")

    @property
    def media_position(self):
        """Position of current playing media in seconds."""
        return self._media_info.get("position")

    @property
    def media_position_updated_at(self):
        """Last time status was updated."""
        return self._last_update

    @property
    def app_name(self):
        """Return the current running application."""
        date = self._media_info.get("date")
        if date is not None:
            return "({})".format(date.year)

    # def set_volume_level(self, volume):
    #    """Set volume level, range 0..1."""
    #    self._player.set_volume_level(volume)

    async def async_turn_on(self):
        """Turn the media player on."""
        # Fire events for automations
        self.hass.bus.async_fire(EVENT_TURN_ON, {ATTR_ENTITY_ID: self.entity_id})
        # Try API and WOL
        self._player.turn_on()

    async def async_turn_off(self):
        """Turn off media player."""
        await self.hass.async_add_executor_job(
            self._player.turn_off,
            self._config_entry.options.get(CONF_POWERMODE, False)
        )

    def volume_up(self):
        """Volume up the media player."""
        self._player.volume_up()

    def volume_down(self):
        """Volume down media player."""
        self._player.volume_down()

    def mute_volume(self, mute):
        """Send mute command."""
        self._player.mute_volume()

    def select_source(self, source):
        """Set the input source."""
        if source in self._content_mapping:
            self._player.start_app(source)

    def media_play_pause(self):
        """Simulate play pause media player."""
        if self._playing:
            self.media_pause()
        else:
            self.media_play()

    def media_play(self):
        """Send play command."""
        self._playing = True
        self._player.media_play()

    def media_pause(self):
        """Send media pause command."""
        if self._player.media_pause():
            self._playing = False

    def media_stop(self):
        """Send media stop command."""
        if self._player.media_stop():
            self._playing = False

    def media_next_track(self):
        """Send next track command."""
        self._player.media_next_track()
        self.schedule_update_ha_state()

    def media_previous_track(self):
        """Send the previous track command."""
        self._player.media_previous_track()
        self.schedule_update_ha_state()

    async def async_play_media(self, media_type, media_id, **kwargs):
        """Play a piece of media."""
        _LOGGER.debug("play request: media_id:{} media_type:{}".format(media_id, media_type))
        if media_source.is_media_source_id(media_id):
            play_item = await media_source.async_resolve_media(
                self.hass, media_id, self.entity_id
            )
            media_id = async_process_play_media_url(self.hass,  play_item.url)
            media_type = play_item.mime_type

        _LOGGER.debug("play: media_id:{} media_type:{}".format(media_id, media_type))

        await self.hass.async_add_executor_job(
            self.play_media,
            media_type,
            media_id
        )

    def play_media(self, media_type, media_id, **kwargs):
        """Play a piece of media."""
        if media_type and media_type == "file":
            self._player.play_file(media_id)
        elif media_type in ZMUSIC_SEARCH_TYPES:
            media_ids = media_id.split(",")
            self._player.play_music(media_ids[0], media_type, media_ids[-1])
        elif "/" in media_type:
            mime_major = media_type.split("/")[0]
            self._player.play_stream(media_id, ZTYPE_MIMETYPE[mime_major])
        else:
            self._player.play_movie(media_id)

    def media_seek(self, position):
        """Send media_seek command to media player."""
        self._player.set_media_position(position, self.media_duration)

    @property
    def media_image_url(self) -> str | None:
        """Image url of current playing media."""
        return self._player.generate_current_image_url()

    async def async_search_media(self, query_string, search_type=None):
        """sets search string for media browser."""
        self._search_query = query_string
        self._search_type = search_type

    async def async_set_subtitle(self):
        """sets or toggles the video subtitle"""
        await self.hass.async_add_executor_job(self._player.set_subtitle)

    async def async_set_audio(self):
        """sets or toggles the audio_track subtitle"""
        await self.hass.async_add_executor_job(self._player.set_audio)

    async def async_browse_media(
        self,
        media_content_type: str | None = None,
        media_content_id: str | None = None,
    ) -> BrowseMedia:
        """Implement the websocket media browsing helper"""

        is_internal = is_internal_request(self.hass)

        return await self.hass.async_add_executor_job(
            browse_media,
            self,
            is_internal,
            media_content_type,
            media_content_id,
        )

    async def async_get_browse_image(
        self,
        media_content_type: str,
        media_content_id: str,
        media_image_id: str | None = None,
    ) -> tuple[bytes | None, str | None]:
        """Get media image from server."""
        image_url = self._player.generate_image_url(
            media_content_id, media_content_type
        )
        if image_url:
            result = await self._async_fetch_image(image_url)
            return result

        return (None, None)
