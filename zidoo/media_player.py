"""Support for interface with Zido Media Player."""
import ipaddress
import logging

from .zidoorc import ZidooRC
from getmac import get_mac_address
import voluptuous as vol

from homeassistant.components.media_player import PLATFORM_SCHEMA, MediaPlayerDevice
from homeassistant.components.media_player.const import (
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
from homeassistant.const import CONF_HOST, CONF_NAME, STATE_OFF, STATE_ON
import homeassistant.helpers.config_validation as cv
from homeassistant.util.json import load_json, save_json

DEFAULT_NAME = 'Zidoo MediaPlayer'

# Map ip to request id for configuring
_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)

CLIENTID_PREFIX = "HomeAssistant"
DEFAULT_NAME = "Zidoo Player"
NICKNAME = "Home Assistant"

SUPPORT_ZIDOO = (
    SUPPORT_NEXT_TRACK
    | SUPPORT_PAUSE	
    | SUPPORT_PLAY
    | SUPPORT_PLAY_MEDIA	
    | SUPPORT_PREVIOUS_TRACK	
    | SUPPORT_SELECT_SOURCE	
    | SUPPORT_STOP	
    | SUPPORT_TURN_OFF	
    | SUPPORT_TURN_ON	
    | SUPPORT_VOLUME_MUTE	
    | SUPPORT_VOLUME_STEP 
)
    #SUPPORT_CLEAR_PLAYLIST
    #SUPPORT_SEEK	
    #SUPPORT_SELECT_SOUND_MODE	
    #SUPPORT_SHUFFLE_SET	
    #SUPPORT_VOLUME_SET	
    

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Zidoo platform."""
    host = config.get(CONF_HOST)
    name = config.get(CONF_NAME)

    add_entities([ZidooPlayerDevice(host, name)])


class ZidooPlayerDevice(MediaPlayerDevice):
    """Representation of a Zido Media."""

    def __init__(self, host, name):
        """Initialize the Zidoo device."""

        self._zidoorc = ZidooRC(host)
        self._name = name
        self._state = STATE_OFF
        self._muted = False
        self._program_name = None
        self._channel_name = None
        self._source = None
        self._source_list = []
        self._original_content_list = []
        self._content_mapping = {}
        self._duration = None
        self._content_uri = None
        self._id = None
        self._playing = False
        self._start_date_time = None
        self._program_media_type = None
        self._min_volume = None
        self._max_volume = None
        self._volume = None

        self._zidoorc.connect(CLIENTID_PREFIX, NICKNAME)
        if self._zidoorc.is_connected():
            self.update()
        else:
            self._state = STATE_OFF

    def update(self):
        """Update TV info."""
        if not self._zidoorc.is_connected():
            if self._zidoorc.get_power_status() != "off":
                self._zidoorc.connect(CLIENTID_PREFIX, NICKNAME)
            if not self._zidoorc.is_connected():
                return

        # Retrieve the latest data.
        try:
            if self._state == STATE_ON:
                # self._refresh_volume()
                self._refresh_channels()
            
            power_status = self._zidoorc.get_power_status()
            if power_status == "on":
                self._state = STATE_ON
                playing_info = self._zidoorc.get_playing_info()
                self._reset_playing_info()
                if playing_info is None or not playing_info:
                    self._channel_name = "Standby"
                    self._program_media_type = MEDIA_TYPE_APP
                else:
                    self._program_name = playing_info.get("title")
                    self._channel_name = playing_info.get("artist")
                    mediatype = playing_info.get("source")
                    #_LOGGER.info("media-type" + str(mediatype))
                    if mediatype and mediatype is not None:
                        if mediatype == 'video':
                            self._program_media_type = MEDIA_TYPE_VIDEO
                        else: 
                            self._program_media_type = MEDIA_TYPE_MUSIC
                    else:
                        self._program_media_type = MEDIA_TYPE_APP
                    #self._source = playing_info.get("source")
                    self._content_uri = playing_info.get("uri")
                    self._duration = playing_info.get("duration")
                    #self._start_date_time = playing_info.get("startDateTime")
            else:
                self._state = STATE_OFF

        except Exception as exception_instance:  # pylint: disable=broad-except
            _LOGGER.error(exception_instance)
            #self._state = STATE_OFF

    def _reset_playing_info(self):
        self._program_name = None
        self._channel_name = None
        self._program_media_type = None
        self._source = None
        self._content_uri = None
        self._duration = None
        self._start_date_time = None

    def _refresh_volume(self):
        """Refresh volume information."""
        volume_info = self._zidoorc.get_volume_info()
        if volume_info is not None:
            self._volume = volume_info.get("volume")
            self._min_volume = volume_info.get("minVolume")
            self._max_volume = volume_info.get("maxVolume")
            self._muted = volume_info.get("mute")

    def _refresh_channels(self):
        if not self._source_list:
            self._content_mapping = self._zidoorc.load_source_list()
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
        
    #@property
    #def volume_level(self):
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
        return SUPPORT_ZIDOO

    @property
    def media_title(self):
        """Title of current playing media."""
        return_value = None
        if self._program_name is not None:
            return_value = self._program_name
            if self._channel_name is not None:
                return_value = self._channel_name + " : " + return_value
        return return_value

    @property
    def media_content_id(self):
        """Content ID of current playing media."""
        return self._program_media_type

    @property
    def media_duration(self):
        """Duration of current playing media in seconds."""
        return self._duration

    #def set_volume_level(self, volume):
    #    """Set volume level, range 0..1."""
    #    self._zidoorc.set_volume_level(volume)

    def turn_on(self):
        """Turn the media player on."""
        self._zidoorc.turn_on()

    def turn_off(self):
        """Turn off media player."""
        self._zidoorc.turn_off()

    def volume_up(self):
        """Volume up the media player."""
        self._zidoorc.volume_up()

    def volume_down(self):
        """Volume down media player."""
        self._zidoorc.volume_down()

    def mute_volume(self, mute):
        """Send mute command."""
        self._zidoorc.mute_volume()

    def select_source(self, source):
        """Set the input source."""
        if source in self._content_mapping:
            uri = self._content_mapping[source]
            self._zidoorc.play_content(uri)

    def media_play_pause(self):
        """Simulate play pause media player."""
        if self._playing:
            self.media_pause()
        else:
            self.media_play()

    def media_play(self):
        """Send play command."""
        self._playing = True
        self._zidoorc.media_play()

    def media_pause(self):
        """Send media pause command to media player."""
        self._playing = False
        self._zidoorc.media_pause()

    def media_next_track(self):
        """Send next track command."""
        self._zidoorc.media_next_track()

    def media_previous_track(self):
        """Send the previous track command."""
        self._zidoorc.media_previous_track()