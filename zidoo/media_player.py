"""Support for interface with Zidoo Media Player."""
import ipaddress
import logging

from .zidoorc import ZidooRC
import voluptuous as vol

from homeassistant.components.media_player import PLATFORM_SCHEMA, MediaPlayerEntity
from homeassistant.components.media_player.const import (
    SUPPORT_BROWSE_MEDIA,
    SUPPORT_CLEAR_PLAYLIST,
    SUPPORT_NEXT_TRACK,
    SUPPORT_PAUSE,
    SUPPORT_PLAY,
    SUPPORT_PLAY_MEDIA,
    SUPPORT_PREVIOUS_TRACK,
    SUPPORT_SEEK,
    SUPPORT_SELECT_SOURCE,
    SUPPORT_SELECT_SOUND_MODE,
    SUPPORT_SHUFFLE_SET,
    SUPPORT_STOP,
    SUPPORT_TURN_OFF,
    SUPPORT_TURN_ON,
    SUPPORT_VOLUME_MUTE,
    SUPPORT_VOLUME_SET,
    SUPPORT_VOLUME_STEP,
    MEDIA_TYPE_MUSIC,
    MEDIA_TYPE_TVSHOW,
    MEDIA_TYPE_MOVIE,
    MEDIA_TYPE_VIDEO,
    MEDIA_TYPE_EPISODE,
    MEDIA_TYPE_CHANNEL,
    MEDIA_TYPE_PLAYLIST,
    MEDIA_TYPE_IMAGE,
    MEDIA_TYPE_URL,
    MEDIA_TYPE_GAME,
    MEDIA_TYPE_APP,
)
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    STATE_IDLE,
    STATE_OFF,
    STATE_PAUSED,
    STATE_PLAYING,
)

import homeassistant.helpers.config_validation as cv
from homeassistant.util.json import load_json, save_json
from homeassistant.util.dt import utcnow

from .media_browser import browse_media  # build_item_response, library_payload
from homeassistant.helpers.network import is_internal_request

DEFAULT_NAME = "Zidoo MediaPlayer"

# Map ip to request id for configuring
_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)

CLIENTID_PREFIX = "HomeAssistant"
NICKNAME = "Home Assistant"
ZIDOO_VIDEOPLAYER = "Media Center"
ZIDOO_ZIDOOPOSTER = "Home Theater 3.0"
ZIDOO_MUSICPLAYER = "Music Player 5.0"

SUPPORT_ZIDOO = (
    SUPPORT_VOLUME_STEP
    | SUPPORT_VOLUME_MUTE
    | SUPPORT_TURN_ON
    | SUPPORT_TURN_OFF
    | SUPPORT_SELECT_SOURCE
    | SUPPORT_BROWSE_MEDIA
)
# SUPPORT_CLEAR_PLAYLIST
# SUPPORT_SEEK
# SUPPORT_SELECT_SOUND_MODE
# SUPPORT_SHUFFLE_SET
# SUPPORT_VOLUME_SET

SUPPORT_MEDIA_MODES = (
    SUPPORT_PAUSE
    | SUPPORT_STOP
    | SUPPORT_PREVIOUS_TRACK
    | SUPPORT_NEXT_TRACK
    | SUPPORT_PLAY
    | SUPPORT_PLAY_MEDIA
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Zidoo platform."""
    host = config.get(CONF_HOST)
    name = config.get(CONF_NAME)

    add_entities([ZidooPlayerDevice(hass, host, name)])


class ZidooPlayerDevice(MediaPlayerEntity):
    """Representation of a Zidoo Media."""

    def __init__(self, hass, host, name):
        """Initialize the Zidoo device."""

        self._player = ZidooRC(host)
        self._hass = hass
        self._name = name
        self._state = STATE_OFF
        self._muted = False
        self._source = None
        self._source_list = []
        self._original_content_list = []
        self._content_mapping = {}
        self._title = None
        self._artist = None
        self._album = None
        self._duration = None
        self._position = None
        self._content_uri = None
        self._id = None
        self._playing = False
        self._program_media_type = None
        self._min_volume = None
        self._max_volume = None
        self._volume = None
        self._last_update = None

        self._player.connect(CLIENTID_PREFIX, NICKNAME)
        if self._player.is_connected():
            self.update()
        else:
            self._state = STATE_OFF

    def update(self):
        """Update TV info."""
        if not self._player.is_connected():
            if self._player.get_power_status() != "off":
                self._player.connect(CLIENTID_PREFIX, NICKNAME)
            if not self._player.is_connected():
                return

        # Retrieve the latest data.
        try:
            power_status = self._player.get_power_status()
            if power_status == "on":
                self._state = STATE_PAUSED
                playing_info = self._player.get_playing_info()
                self._reset_playing_info()
                if playing_info is None or not playing_info:
                    self._channel_name = "Standby"
                    self._program_media_type = MEDIA_TYPE_APP
                else:
                    self._title = playing_info.get("title")
                    self._artist = playing_info.get("artist")
                    mediatype = playing_info.get("source")
                    if mediatype and mediatype is not None:
                        if mediatype == "video":
                            self._program_media_type = MEDIA_TYPE_VIDEO
                            self._source = ZIDOO_VIDEOPLAYER
                        else:
                            self._program_media_type = MEDIA_TYPE_MUSIC
                            self._source = ZIDOO_MUSICPLAYER
                    else:
                        self._program_media_type = MEDIA_TYPE_APP
                    status = playing_info.get("status")
                    if status and status is not None:
                        if status == 1 or status == True:
                            self._state = STATE_PLAYING
                    self._duration = playing_info.get("duration")
                    self._position = playing_info.get("position")
                    self._content_uri = playing_info.get("uri")
                    self._last_update = utcnow()
                self._refresh_channels()
            else:
                self._state = STATE_OFF

        except Exception as exception_instance:  # pylint: disable=broad-except
            _LOGGER.error(exception_instance)
            # self._state = STATE_OFF

    def _reset_playing_info(self):
        self._title = None
        self._artist = None
        self._album = None
        self._program_media_type = None
        self._source = None
        self._content_uri = None
        self._duration = None
        self._position = None
        self._start_date_time = None

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
            self._source_list = []
            for key in self._content_mapping:
                self._source_list.append(key)

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
        self._program_media_type

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
        title = self._title
        if self._artist is not None:
            title = self._artist + " : " + title
        return title

    @property
    def media_artist(self):
        """Artist of current playing media."""
        return self._artist

    @property
    def media_album_name(self):
        """Album of current playing media."""
        return self._album

    @property
    def media_content_id(self):
        """Content ID of current playing media."""
        return self._program_media_type

    @property
    def media_duration(self):
        """Duration of current playing media in seconds."""
        return self._duration

    @property
    def media_position(self):
        """Position of current playing media in seconds."""
        return self._position

    @property
    def media_position_updated_at(self):
        """Last time status was updated."""
        return self._last_update

    # def set_volume_level(self, volume):
    #    """Set volume level, range 0..1."""
    #    self._player.set_volume_level(volume)

    def turn_on(self):
        """Turn the media player on."""
        self._player.turn_on()

    def turn_off(self):
        """Turn off media player."""
        self._player.turn_off()

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
            # uri = self._content_mapping[source]
            # play_content(uri)

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
        """Send media pause command to media player."""
        self._playing = False
        self._player.media_pause()

    def media_next_track(self):
        """Send next track command."""
        self._player.media_next_track()

    def media_previous_track(self):
        """Send the previous track command."""
        self._player.media_previous_track()

    def play_media(self, media_type, media_id, **kwargs):
        """Play a piece of media."""
        if media_type and media_type == 'movie':
            self._player.play_movie(media_id)
        else:
            self._player.play_content(media_id)

    async def async_browse_media(self, media_content_type=None, media_content_id=None):
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
        self, media_content_type, media_content_id, media_image_id=None
    ):
        """Get media image from server."""
        image_url = self._player.generate_movie_image_url(media_content_id)
        if image_url:
            result = await self._async_fetch_image(image_url)
            return result

        return (None, None)
