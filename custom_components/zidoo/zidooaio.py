"""Zidoo Remote Control API by Wizmo.

References:
    oem v1: https://www.zidoo.tv/Support/developer/
    oem v2: https://apidoc.zidoo.tv
"""

import asyncio
from datetime import datetime, timezone
import time
import logging
import socket
import struct
import urllib.parse
from asyncio import Lock, Task
from functools import wraps

from aiohttp import ClientError, ClientOSError, ClientSession, CookieJar
from yarl import URL

_LOGGER = logging.getLogger(__name__)

VERSION = "0.4.2"
TIMEOUT = 5  # default timeout
TIMEOUT_INFO = 1  # for playing info
TIMEOUT_SEARCH = 10  # for searches
RETRIES = 3  # default retries
CONF_PORT = 9529  # default api port
DEFAULT_COUNT = 250  # default list limit
ERROR_OS_WAIT = 0.5  # wait time for OS errors
MEDIA_STATUS_GRACE = 60.0  # seconds to keep stale media
CONNECT_LOCK_TIMEOUT = 20.0 


class ZidooEndpoints:
    """Consolidated Zidoo API endpoints."""
    GET_SMB_DEVICES = "ZidooFileControl/v2/getSavedSmbDevices"
    GET_FILES = "ZidooFileControl/v2/getFiles"
    GET_MODEL = "ZidooControlCenter/getModel"
    SEND_KEY = "ZidooControlCenter/RemoteControl/sendkey"
    VIDEO_PLAY_STATUS = "ZidooVideoPlay/getPlayStatus"
    MUSIC_PLAY_STATUS = "ZidooMusicControl/getPlayStatus"
    MUSIC_PLAY_STATUS_V2 = "ZidooMusicControl/v2/getState"
    POSTER_AGGREGATION_FILE = "ZidooPoster/v2/getAggregationOfFile"
    VIDEO_PLAY_MODES = "ZidooVideoPlay/getPlayModeList"
    VIDEO_SUBTITLE_LIST = "ZidooVideoPlay/getSubtitleList"
    VIDEO_SET_SUBTITLE = "ZidooVideoPlay/setSubtitle"
    VIDEO_AUDIO_LIST = "ZidooVideoPlay/getAudioList"
    VIDEO_SET_AUDIO = "ZidooVideoPlay/setAudio"
    VIDEO_ZOOM_LIST = "VideoPlay/getZoomList"
    VIDEO_SET_ZOOM = "VideoPlay/setZoom"
    VIDEO_CHANGE_VIDEO = "ZidooVideoPlay/changevideo"
    VIDEO_CHANGE_STATUS = "ZidooVideoPlay/changeStatus"
    MUSIC_IO_LIST = "ZidooMusicControl/v2/getInputAndOutputList"
    MUSIC_SET_IO = "ZidooMusicControl/v2/setOutInputList"
    GET_APPS = "ZidooControlCenter/Apps/getApps"
    OPEN_APP = "ZidooControlCenter/Apps/openApp"
    GET_DEVICES = "ZidooFileControl/getDevices"
    POSTER_AGGREGATIONS = "ZidooPoster/v2/getAggregations"
    POSTER_COLLECTION = "ZidooPoster/getCollection"
    POSTER_DETAIL = "ZidooPoster/v2/getDetail"
    MUSIC_GET_SINGLE = "MusicControl/v2/getSingleMusics"
    MUSIC_GET_ALBUM_MUSICS = "MusicControl/v2/getAlbumMusics"
    MUSIC_GET_ALBUM = "MusicControl/v2/getAlbums"
    MUSIC_GET_ARTIST_MUSICS = "MusicControl/v2/getArtistMusics"
    MUSIC_GET_ARTISTS = "MusicControl/v2/getArtists"
    MUSIC_GET_PLAY_QUEUE = "MusicControl/v2/getPlayQueue"
    MUSIC_GET_FAVORITES = "MusicControl/v2/getFavorites"
    MUSIC_GET_SONGLIST_MUSICS = "MusicControl/v2/getSongListMusics"
    MUSIC_GET_SONGLISTS = "MusicControl/v2/getSongLists"
    POSTER_SEARCH = "ZidooPoster/v2/searchAggregation"
    MUSIC_SEARCH = "MusicControl/v2/searchMusic"
    MUSIC_SEARCH_ALBUM = "MusicControl/v2/searchAlbum"
    MUSIC_SEARCH_ARTIST = "MusicControl/v2/searchArtist"
    MUSIC_LOOP_MODE = "ZidooMusicControl/v2/setLoopMode"
    FILE_OPEN = "ZidooFileControl/openFile"
    FILE_OPEN_V2 = "ZidooFileControl/v2/openFile"
    POSTER_PLAY_VIDEO = "ZidooPoster/PlayVideo"
    MUSIC_PLAY_MUSIC = "MusicControl/v2/playMusic"
    MUSIC_PLAY_MUSICS = "MusicControl/v2/playMusics"
    VIDEO_PLAYLIST = "VideoPlay/getPlaylist"
    FILE_LIST = "ZidooFileControl/getFileList"
    FILE_HOST = "ZidooFileControl/getHost"
    POSTER_GET_POSTER = "ZidooPoster/v2/getPoster"
    MUSIC_GET_IMAGE = "ZidooMusicControl/v2/getImage"
    POSTER_GET_BACKDROP = "ZidooPoster/v2/getBackdrop"
    MUSIC_PLAY_PAUSE = "MusicControl/v2/playOrPause"
    MUSIC_PLAY_NEXT = "MusicControl/v2/playNext"
    MUSIC_PLAY_LAST = "MusicControl/v2/playLast"
    VIDEO_SEEK = "ZidooVideoPlay/seekTo"
    MUSIC_SEEK = "ZidooMusicControl/seekTo"


"""Remote Control Button keys"""
ZKEY_BACK = "Key.Back"
ZKEY_CANCEL = "Key.Cancel"
ZKEY_HOME = "Key.Home"
ZKEY_UP = "Key.Up"
ZKEY_DOWN = "Key.Down"
ZKEY_LEFT = "Key.Left"
ZKEY_RIGHT = "Key.Right"
ZKEY_OK = "Key.Ok"
ZKEY_SELECT = "Key.Select"
ZKEY_STAR = "Key.Star"
ZKEY_POUND = "Key.Pound"
ZKEY_DASH = "Key.Dash"
ZKEY_MENU = "Key.Menu"
ZKEY_MEDIA_PLAY = "Key.MediaPlay"
ZKEY_MEDIA_PLAY_PAUSE = "Key.MediaPlay.Pause"
ZKEY_MEDIA_STOP = "Key.MediaStop"
ZKEY_MEDIA_PAUSE = "Key.MediaPause"
ZKEY_MEDIA_NEXT = "Key.MediaNext"
ZKEY_MEDIA_PREVIOUS = "Key.MediaPrev"
ZKEY_MEDIA_BACKWARDS = "Key.MediaBackward"
ZKEY_MEDIA_FORWARDS = "Key.MediaForward"
ZKEY_NUM_0 = "Key.Number_0"
ZKEY_NUM_1 = "Key.Number_1"
ZKEY_NUM_2 = "Key.Number_2"
ZKEY_NUM_3 = "Key.Number_3"
ZKEY_NUM_4 = "Key.Number_4"
ZKEY_NUM_5 = "Key.Number_5"
ZKEY_NUM_6 = "Key.Number_6"
ZKEY_NUM_7 = "Key.Number_7"
ZKEY_NUM_8 = "Key.Number_8"
ZKEY_NUM_9 = "Key.Number_9"
ZKEY_USER_A = "Key.UserDefine_A"
ZKEY_USER_B = "Key.UserDefine_B"
ZKEY_USER_C = "Key.UserDefine_C"
ZKEY_USER_D = "Key.UserDefine_D"
ZKEY_MUTE = "Key.Mute"
ZKEY_VOLUME_UP = "Key.VolumeUp"
ZKEY_VOLUME_DOWN = "Key.VolumeDown"
ZKEY_POWER_ON = "Key.PowerOn"
ZKEY_INFO = "Key.Info"
ZKEY_RECORD = "Key.Record"
ZKEY_PAGE_UP = "Key.PageUP"
ZKEY_PAGE_DOWN = "Key.PageDown"
ZKEY_SUBTITLE = "Key.Subtitle"
ZKEY_AUDIO = "Key.Audio"
ZKEY_REPEAT = "Key.Repeat"
ZKEY_MOUSE = "Key.Mouse"
ZKEY_POPUP_MENU = "Key.PopMenu"
ZKEY_APP_MOVIE = "Key.movie"
ZKEY_APP_MUSIC = "Key.music"
ZKEY_APP_PHOTO = "Key.photo"
ZKEY_APP_FILE = "Key.file"
ZKEY_LIGHT = "Key.light"
ZKEY_RESOLUTION = "Key.Resolution"
ZKEY_POWER_REBOOT = "Key.PowerOn.Reboot"
ZKEY_POWER_OFF = "Key.PowerOn.Poweroff"
ZKEY_POWER_STANDBY = "Key.PowerOn.Standby"
ZKEY_PICTURE_IN_PICTURE = "Key.Pip"
ZKEY_SCREENSHOT = "Key.Screenshot"
ZKEY_APP_SWITCH = "Key.APP.Switch"
ZKEY_APP_3D = "Key.APP.3D"
ZKEY_APP_HDMI_IN = "Key.APP.HdmiIn"

ZKEYS = [
    ZKEY_BACK,
    ZKEY_CANCEL,
    ZKEY_HOME,
    ZKEY_UP,
    ZKEY_DOWN,
    ZKEY_LEFT,
    ZKEY_RIGHT,
    ZKEY_OK,
    ZKEY_SELECT,
    ZKEY_STAR,
    ZKEY_POUND,
    ZKEY_DASH,
    ZKEY_MENU,
    ZKEY_MEDIA_PLAY,
    ZKEY_MEDIA_PLAY_PAUSE,
    ZKEY_MEDIA_STOP,
    ZKEY_MEDIA_PAUSE,
    ZKEY_MEDIA_NEXT,
    ZKEY_MEDIA_PREVIOUS,
    ZKEY_MEDIA_BACKWARDS,
    ZKEY_MEDIA_FORWARDS,
    ZKEY_NUM_0,
    ZKEY_NUM_1,
    ZKEY_NUM_2,
    ZKEY_NUM_3,
    ZKEY_NUM_4,
    ZKEY_NUM_5,
    ZKEY_NUM_6,
    ZKEY_NUM_7,
    ZKEY_NUM_8,
    ZKEY_NUM_9,
    ZKEY_USER_A,
    ZKEY_USER_B,
    ZKEY_USER_C,
    ZKEY_USER_D,
    ZKEY_MUTE,
    ZKEY_VOLUME_UP,
    ZKEY_VOLUME_DOWN,
    ZKEY_POWER_ON,
    ZKEY_INFO,
    ZKEY_RECORD,
    ZKEY_PAGE_UP,
    ZKEY_PAGE_DOWN,
    ZKEY_SUBTITLE,
    ZKEY_AUDIO,
    ZKEY_REPEAT,
    ZKEY_MOUSE,
    ZKEY_POPUP_MENU,
    ZKEY_APP_MOVIE,
    ZKEY_APP_MUSIC,
    ZKEY_APP_PHOTO,
    ZKEY_APP_FILE,
    ZKEY_LIGHT,
    ZKEY_RESOLUTION,
    ZKEY_POWER_REBOOT,
    ZKEY_POWER_OFF,
    ZKEY_POWER_STANDBY,
    ZKEY_PICTURE_IN_PICTURE,
    ZKEY_SCREENSHOT,
    ZKEY_APP_SWITCH,
    ZKEY_APP_3D,
    ZKEY_APP_HDMI_IN,
]

"""Movie Player entry types."""
ZTYPE_VIDEO = 0
ZTYPE_MOVIE = 1
ZTYPE_COLLECTION = 2
ZTYPE_TV_SHOW = 3
ZTYPE_TV_SEASON = 4
ZTYPE_TV_EPISODE = 5
ZTYPE_OTHER = 6

ZTYPE_NAMES = {
    ZTYPE_VIDEO: "video",
    ZTYPE_MOVIE: "movie",
    ZTYPE_COLLECTION: "collection",
    ZTYPE_TV_SHOW: "tvshow",
    ZTYPE_TV_SEASON: "tvseason",
    ZTYPE_TV_EPISODE: "tvepisode",
    ZTYPE_OTHER: "other",
}

ZCONTENT_VIDEO = "Video Player"
ZCONTENT_MUSIC = "Music Player"
ZCONTENT_NONE = None

# """v1 Movie Player search keys (getVideolist)."""
# ZVIDEO_FILTER_TYPES = {
#    "all": 0,
#    "favorite": 1,
#    "watching": 2,
#    "movie": 3,
#    "tvshow": 4,
#    "sd": 5,
#    "bluray": 6,
#    "4k": 7,
#    "3d": 8,
#    "children": 9,
#    "recent": 10,
#    "unwatched": 11,
#    "other": 12,
# ?"dolby": 13
# }

"""v2 Movie Player search keys (getAggregations)"""
ZVIDEO_FILTER_TYPES = {
    "all": 0,
    "favorite": 1,
    "watching": 2,
    "collections": 3,
    "tvshow": 4,
    "bluray": 5,
    "4k": 6,
    "3d": 7,
    "children": 8,
    "recent": 9,
    "unwatched": 10,
    "other": 11,
    "movie": 12,
    # ?"dolby": 13,
    # ?"hdr": 14,
}

ZVIDEO_SEARCH_TYPES = {
    # "all": -1,    # combined results
    "video": 0,  # all movies tvshows and collections
    "movie": 1,
    "tvshow": 2,
    "collection": 3,
}

ZMUSIC_SEARCH_TYPES = {"music": 0, "album": 1, "artist": 2, "playlist": 3}

"""File System devicce type names"""
ZDEVICE_FOLDER = 1000
ZDEVICE_NAMES = {
    1000: "hhd",
    1001: "usb",
    1002: "usb",
    1003: "tf",
    1004: "nfs",
    1005: "smb",
}

ZFILETYPE_NAMES = {
    0: "folder",
    1: "music",
    2: "movie",
    3: "Image",
    4: "txt",
    5: "apk",
    6: "pdf",
    7: "doc",
    8: "xls",
    9: "ppt",
    10: "web",
    11: "zip",
    # default: "other",
}

ZTYPE_MIMETYPE = {
    "image": 3,
    "video": 2,
    "audio": 2,  # 1 is Music Player but upnp needs dms server
    "other": 0,
    "default": 4,
    "application": 4,  # 0 always asks (and can be usd to reset starup app)
}

ZUPNP_SERVERNAME = "zidoo-rc"

ZMEDIA_TYPE_ARTIST = "artist"
ZMEDIA_TYPE_ALBUM = "album"
ZMEDIA_TYPE_PLAYLIST = "playlist"
ZMEDIA_PLAYLIST = ["favorites", "playing"]

ZMUSIC_IMAGETYPE = {0: 0, 1: 1, 2: 0, 3: 0, 4: 1}
ZMUSIC_IMAGETARGET = {0: 16, 1: 16, 2: 32, 3: 16, 4: 32}
ZMUSIC_PLAYLISTTYPE = {
    ZMEDIA_TYPE_ARTIST: 3,
    ZMEDIA_TYPE_ALBUM: 4,
    ZMEDIA_TYPE_PLAYLIST: 5,
}

ZSTATE_STOPPED = 0
ZSTATE_PLAYING = 1
ZSTATE_PAUSED = 2


def NUM_STR(num, dec, dimen):
    """Converts to a number to k/K or M (bps/Hz)."""
    if num > 1000000:
        dimen = "M" + dimen
        num = num / 1000000
    elif num > 1000:
        dimen = "K" + dimen if dimen == "bps" else "k" + dimen
        num = num / 1000

    # check if num is not a whole number and if so, round to required decimals
    if num % 1 == 0:
        num = round(num)
    else:
        num = round(num, dec)

    return str(num) + " " + dimen


class ZidooRC:
    """Zidoo Media Player Remote Control."""

    def __init__(self, host: str, psk: str = "", mac: str = "") -> None:
        """Initialize the Zidoo class.

        Parameters
            host:
                IP address
            mac:
                address is optional and can be used to manually assign the WOL address.
            psk:
                authorization password key.  If not assigned, standard basic auth is used.
        """

        self._host = f"{host}:{CONF_PORT}"
        self._mac = mac
        self._mac_addresses = set()
        if mac:
            self._mac_addresses.add(mac)
            
        self._psk = psk
        self._session: ClientSession | None = None
        self._cookies = None
        self._content_mapping = []
        self._current_source = ""
        self._app_list = {}
        self._power_status = False
        self._video_id = -1
        self._music_id = -1
        self._music_type = -1
        self._last_video_path = None
        self._movie_info = {}
        self._current_subtitle = 0
        self._current_audio = 0
        self._current_zoom: int = 0
        self._current_playmode = 0
        self._song_list = []
        self._audio_output_list = []

        self._connect_lock = Lock()
        self._last_update = None
        self._last_media_info = {}
        self._subtitles_tracks = []
        self._audio_tracks = []
        self._last_video_id_lookup = 0.0

    async def _init_device(self):
        """Initialize device on connect."""
        response = await self._req_json(ZidooEndpoints.GET_SMB_DEVICES)
        if response:
            # attempt connection to each saved network share
            data = response.get("data")
            if data and data["count"] > 0:
                for item in data["list"]:
                    url = urllib.parse.quote(item.get("url"), safe="")
                    await self._req_json(f"{ZidooEndpoints.GET_FILES}?requestCount=100&startIndex=0&sort=0&url={url}")

        # gets current song list (and appears to initialize network shared on old devices)
        await self.get_music_playlist()
        _LOGGER.debug("SONG_LIST: %s", self._song_list)

        # get audio_output_list to initialize v1/v2 alternative
        await self.get_audio_output()

    async def connect(self):
        """Connect to player and get authentication cookie.

        Returns:
            json
                raw api response if successful.
        """
        if self._connect_lock.locked():
            return None

        await self._connect_lock.acquire()
        try:
            response = await self.get_system_info(log_errors=False)

            if response and response.get("status") == 200:
                _LOGGER.debug("connected: %s", response)
                
                if response.get("net_mac"):
                    self._mac_addresses.add(response.get("net_mac"))
                if response.get("wif_mac"):
                    self._mac_addresses.add(response.get("wif_mac"))
                
                if not self._mac and self._mac_addresses:
                    self._mac = list(self._mac_addresses)[0]
                    
                self._power_status = True
                await self._init_device()
                return response
            return None
        finally:
            self._connect_lock.release()

    async def disconnect(self) -> None:
        """Async Close connection."""
        if self._session:
            await self._session.close()
        self._psk = None
        self._session = None

    def is_connected(self) -> bool:
        """Check connection status.

        Returns:
            bool
                True if connected.
        """
        return self._cookies is not None

    def _wakeonlan(self) -> None:
        """Send WOL command. to known mac addresses."""
        messages = []
        for mac in self._mac_addresses:
            addr_byte = mac.split(":")
            if len(addr_byte) == 6:
                hw_addr = struct.pack("BBBBBB", *[int(b, 16) for b in addr_byte])
                messages.append(b"\xff" * 6 + hw_addr * 16)
                
        if messages:
            socket_instance = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            socket_instance.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            for msg in messages:
                socket_instance.sendto(msg, ("<broadcast>", 9))
            socket_instance.close()

    async def _send_key(self, key: str, log_errors: bool = False) -> bool:
        """Async Send Remote Control button command to device.

        Parameters
            key: str
                remote control key command (see ZKEY list)
            log_errors: bool
                suppresses error logging if False
        Returns
            True if successful
        """
        params = {"key": key}
        response = await self._req_json(ZidooEndpoints.SEND_KEY, params, log_errors, max_retries=0)
        if response and response.get("status") == 200:
            return True
        return False

    async def _req_json(
        self,
        url: str,
        params: dict | None = None,
        log_errors: bool = True,
        timeout: int = TIMEOUT,
        max_retries: int = RETRIES,
    ):
        """Async Send request command via HTTP json to player.

        Parameters
            url: str
                api call
            params: str
                api parameters
            log_errors: bool
                suppresses error logging if False
            max_retries
                reties on response errors
            timeout
                request timeout in seconds
        Returns
            json
                raw API response
        """
        while max_retries >= 0:
            response = await self._send_cmd(url, params, log_errors, timeout)

            if response and response.status == 200:
                result = await response.json(content_type=None)
                # _LOGGER.debug("url:%s params:%s result:%s",str(url),str(params),str(result.get("status")))
                if result:
                    # player can report 804 when switching media. force retry
                    if ZidooEndpoints.VIDEO_PLAY_STATUS not in url or result.get("status") != 804:
                        return result

            if max_retries > 0:
                _LOGGER.warning("[W] Retry %d: url:%s", max_retries, url)
                await asyncio.sleep(0.5)
            max_retries -= 1

        # clear cookies to show not connected
        if self._cookies is not None:
            _LOGGER.debug("No response from player! Showing not connected")
            self._cookies = None
        return None

    async def _send_cmd(
        self,
        url: str,
        params: dict | None = None,
        log_errors: bool = True,
        timeout: int = TIMEOUT,
    ):
        """Async Send request command via HTTP json to player.

        Parameters
            url: str
                api call.
            params: str
                api parameters.
            log_errors: bool
                suppresses error logging if False
            timeout
                request timeout in seconds
        Returns
            response
                raw API response
        """
        if self._session is None:
            self._session = ClientSession(
                cookie_jar=CookieJar(unsafe=True, quote_cookie=False)
            )

        headers = {"Cache-Control": "no-cache", "Connection": "keep-alive"}
        if self._psk:
            headers["X-Auth-PSK"] = self._psk

        full_url = f"http://{self._host}/{url}"
        response = None

        try:
            response = await self._session.get(
                URL(full_url, encoded=True),
                params=params,
                cookies=self._cookies,
                timeout=timeout,
                headers=headers,
            )

        except ClientError as err:
            if log_errors and self._power_status:
                _LOGGER.info("[I] Client Error: %s", str(err))
            
            if isinstance(err, ClientOSError):
                _LOGGER.warning("[%s] OS error, waiting %ss", self._host, ERROR_OS_WAIT)
                try:
                    await asyncio.sleep(ERROR_OS_WAIT)
                    response = await self._session.get(
                        URL(full_url, encoded=True), params=params, cookies=self._cookies, timeout=timeout, headers=headers
                    )
                except Exception:
                    pass
        except ConnectionError as err:
            if log_errors and self._power_status:
                _LOGGER.info("[I] Connect Error: %s", str(err))

        except asyncio.exceptions.TimeoutError as err:
            if log_errors and self._power_status:
                _LOGGER.warning("[W] Timeout Error: %s", str(err))

        if response is not None and response.status == 200:
            self._cookies = response.cookies
        return response

    async def get_source(self) -> str:
        """Async Return last known app."""
        return self._current_source

    async def load_source_list(self) -> dict:
        """Async Return app list."""
        return await self.get_app_list()

    def _should_keep_stale_media(self) -> bool:
        if not self._last_media_info or self._last_update is None:
            return False
        # Keep metadata in case last update was within MEDIA_STATUS_GRACE seconds
        now = datetime.now(timezone.utc)
        last = self._last_update
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
        return (now - last).total_seconds() <= MEDIA_STATUS_GRACE

    async def get_playing_info(self):
        """Async Get playing information of active app.

        Returns:
            json (if successful)
                source: music = music player, video = vodeo player
                status: True if playing
                uri: path to current file
                title: title (filename)
                duration: length in ms
                position: position in ms
                artist: artist name(music only)
                track: track title (music only)
                type: ??
                movie_name: movie title (movie only)
                tag: tag line (movie only)
                date: ase date (movie only)
                episode: episode number (tv only)
                episode_name: episode title (tv only)
                season: season number (tv only)
                season_name: season title (tv only)
                series_name: series title (tv only)
        """
        return_value = {}

        response = await self._get_video_playing_info()
        if response is not None:
            return_value = response
            return_value["source"] = "video"
            self._current_source = ZCONTENT_VIDEO
            self._last_update = datetime.now(timezone.utc)
            self._last_media_info = {**return_value, **self._movie_info}
            return self._last_media_info

        if self._audio_output_list:
            response = await self._get_music_playing_info_v2()
        else:
            response = await self._get_music_playing_info()

        if response is not None:
            return_value = response
            return_value["source"] = "music"

            self._current_source = ZCONTENT_MUSIC
            self._last_update = datetime.now()
            self._last_media_info = return_value
            return return_value

        if not return_value and self._should_keep_stale_media():
            return self._last_media_info

        self._current_source = ZCONTENT_NONE
        return return_value

    async def _get_video_playing_info(self):
        """Async Get information from built in video player."""
        return_value = {}
        response = await self._req_json(ZidooEndpoints.VIDEO_PLAY_STATUS, log_errors=False, timeout=TIMEOUT_INFO)

        if response is not None: 
            if response.get("status") == 200:
                if response.get("subtitle"):
                    self._current_subtitle = response["subtitle"].get("index")
                    return_value["subtitle"] = response["subtitle"].get("information")
                if response.get("audio"):
                    self._current_audio = response["audio"].get("index")
                    # return_value["audio"] = response["audio"].get("information")
                if response.get("zoom"):
                    self._current_zoom = response["zoom"].get("index")
                    return_value["zoom"] = response["zoom"].get("information")
                if response.get("playMode"):
                    self._current_playmode = response["playMode"].get("index")
                    return_value["playmode"] = response["playMode"].get("information")
                if response.get("video"):
                    result = response.get("video")
                    return_value["status"] = result.get("status") == ZSTATE_PLAYING
                    return_value["title"] = result.get("title")
                    return_value["uri"] = result.get("path")
                    return_value["duration"] = result.get("duration")
                    return_value["position"] = result.get("currentPosition")
                    return_value["width"] = result.get("width")
                    return_value["height"] = result.get("height")
                    return_value["fps"] = result.get("fps")
                    return_value["bitrate"] = result.get("bitrate")
                    return_value["audio"] = result.get("audioInfo")
                    return_value["video"] = result.get("output")
                    
                    # Caching the last video path and checking if it has changed or if we need to look up the video ID again
                    current_uri = return_value["uri"]

                    if current_uri and (current_uri != self._last_video_path or (self._video_id <= 0 and (time.time() - self._last_video_id_lookup) >= 10)):
                        # Clear movie info if the current URI has changed since the last lookup
                        if current_uri != self._last_video_path:
                            self._movie_info = {}
                            
                        self._last_video_path = current_uri
                        self._last_video_id_lookup = time.time()
                        self._video_id = await self._get_id_from_uri(self._last_video_path)
                    
                    return_value["id"] = self._video_id
                    return return_value
            elif response.get("status") == 806:
                # No video is playing (resource does not exist).
                # Reset the stale timer.
                self._last_update = None
        # _LOGGER.debug("video play info: %s", str(response))
        return None

    async def _get_id_from_uri(self, uri: str) -> int:
        """Async Return movie id from the path."""
        movie_id = 0
        movie_info = {}

        response = await self._req_json(f"{ZidooEndpoints.POSTER_AGGREGATION_FILE}?path={urllib.parse.quote(uri)}")

        if response:
            movie_info["type"] = response.get("type")
            result = response.get("movie")
            if result is not None:
                movie_id = result.get("id")
                movie_info["movie_name"] = result.get("name")
                movie_info["tag"] = result["aggregation"].get("tagLine")
                release = result["aggregation"].get("releaseDate")
                if release:
                    try:
                        movie_info["date"] = datetime.strptime(release, "%Y-%m-%d" if  "-" in release else '$Y')  
                    except ValueError:
                        _LOGGER.debug("skipping date due to bad format!")
                        pass
                tmdb = result["aggregation"].get("tmdbId")
                if tmdb:
                    movie_info["tmdb_id"] = tmdb
                imdb = result["aggregation"].get("imdbId")
                if imdb:
                    movie_info["imdb_id"] = imdb
            result = response.get("episode")
            if result is not None:
                movie_id = result.get("id")
                movie_info["episode"] = result["aggregation"].get("episodeNumber")
                movie_info["episode_name"] = result["aggregation"].get("name")
            result = response.get("season")
            if result is not None:
                movie_info["season"] = result["aggregation"].get("seasonNumber")
                movie_info["season_name"] = result["aggregation"].get("name")
                movie_info["series_name"] = result["aggregation"].get("tvName")
            if not movie_id:
                result = response.get("video")
                if result is not None:
                    movie_id = result.get("parentId")

            self._movie_info = movie_info

        _LOGGER.debug("new media detected (%s): %s", str(movie_id), str(movie_info))
        return movie_id

    async def _get_music_playing_info(self):
        """Async Get information from built in Music Player."""
        return_value = {}
        response = await self._req_json(ZidooEndpoints.MUSIC_PLAY_STATUS, log_errors=False, timeout=TIMEOUT_INFO)
        if response is not None and response.get("status") == 200:
            return_value["status"] = (
                ZSTATE_PAUSED if response.get("isPlay") else ZSTATE_STOPPED
            )
            result = response.get("music")
            if result is not None:
                return_value["title"] = result.get("title")
                return_value["artist"] = result.get("artist")
                return_value["track"] = result.get("number")
                return_value["date"] = result.get("date")
                return_value["uri"] = result.get("uri")
                return_value["bitrate"] = result.get("bitrate")
                return_value["audio"] = "{}: {} channels {} bits {} Hz".format(
                    result.get("extension"),
                    result.get("channels"),
                    result.get("bits"),
                    result.get("SampleRate"),
                )
                music_id = int(result.get("id"))
                if music_id != self._music_id:
                    _LOGGER.debug("music play info %s", str(response))
                    self._music_id = music_id
                return_value["id"] = self._music_id
                self._music_type = result.get("type")

                result = response.get("state")
                return_value["duration"] = result.get("duration")
                return_value["position"] = result.get("position")
                if result is not None and result.get("playing"):
                    return_value["status"] = ZSTATE_PLAYING

                return return_value
        return None

    async def _get_music_playing_info_v2(self):
        """Async Get Eversolo information from built in Music Player using API V2."""
        return_value = {}
        response = await self._req_json(ZidooEndpoints.MUSIC_PLAY_STATUS_V2, log_errors=False, timeout=TIMEOUT_INFO)
        return_value["status"] = ZSTATE_STOPPED
        if response is not None and response.get("state") != 0:
            # common return values for LOCAL and DLNA
            return_value["duration"] = response.get("duration")
            return_value["position"] = response.get("position")
            return_value["status"] = (
                ZSTATE_PLAYING if response.get("state") == 3 else ZSTATE_PAUSED
            )

            # data depends on source
            eversolo = response.get("everSoloPlayInfo")
            result = response.get("playingMusic")
            if result is not None:
                album_art = result.get("albumArt")
                music_id = str(album_art) if album_art else int(result.get("id"))
                if music_id != self._music_id:
                    _LOGGER.debug("music play info v2 %s", str(response))
                    self._music_id = music_id
                return_value["id"] = self._music_id
                self._music_type = int(result.get("type"))

                return_value["album"] = result.get("album")
                return_value["artist"] = result.get("artist")
                return_value["title"] = result.get("title")
                return_value["track"] = result.get("number")
                return_value["date"] = result.get("date")
                return_value["uri"] = result.get("uri")
                return_value["bitrate"] = result.get("bitrate")

                extension = result.get("extension")
                channels = result.get("channels")
                bits = result.get("bits")
                samplerate = result.get("SampleRate")

                if eversolo:
                    eversolo_audio = eversolo.get("everSoloPlayAudioInfo")
                    eversolo_volume = response.get("volumeData")
                    # source = eversolo.get("playTypeSubtitle") if eversolo else "LOCAL"
                    if self._music_type == 1:  # source == "LOCAL"
                        # fix for multichannel SACD info
                        # TODO: is channelsSecond in playingInfo or everSoloPlayInfo/everSoloPlayAudioInfo
                        sacd_area = (
                            eversolo_volume.get("sacdArea") if eversolo_volume else -1
                        )
                        channels2 = result.get("channelsSecond")
                        if (
                            extension == "SACD"
                            and sacd_area == 1
                            and channels2 is not None
                        ):
                            channels = channels2

                    elif eversolo_audio:  # source == "DLNA":
                        if not return_value["album"]:
                            return_value["album"] = eversolo_audio.get("albumName")
                        if not return_value["artist"]:
                            return_value["artist"] = eversolo_audio.get("artistName")
                        if not return_value["title"]:
                            return_value["title"] = eversolo_audio.get("songName")

                        # fix for DLNA audio info
                        # extension = (result.get("audioDecodec"),) # not in api ref
                        channels = eversolo_audio.get("audioChannels")
                        samplerate = eversolo_audio.get("audioSampleRate")
                        bits = eversolo_audio.get("audioBitsPerSample")
                        bitrate = samplerate * channels * bits
                        return_value["bitrate"] = NUM_STR(bitrate, 2, "bps")

                return_value["audio"] = (
                    f"{extension}: {channels} channels {bits} bits {samplerate}"
                )
            return return_value
        return None

    async def get_play_modes(self):
        """Async Get the play-mode list.

        Returns:
            json
                raw api response when successful
        """
        response = await self._req_json(ZidooEndpoints.VIDEO_PLAY_MODES)
        if response is not None and response.get("status") == 200:
            return response
        return None

    def _next_data(self, data, index: int) -> int:
        """Toggle list."""
        temp = iter(data)
        for key in temp:
            if key == index:
                return next(temp, 0)
        return 0

    async def get_subtitle_list(self, log_errors=True) -> list:
        """Async Get subtitle list.

        Returns:
            dictionary list
        """
        response = await self._req_json(ZidooEndpoints.VIDEO_SUBTITLE_LIST, log_errors=log_errors)
        if response is not None and response.get("status") == 200:
            self._subtitles_tracks = response.get("subtitles", [])
            return self._subtitles_tracks
        return []

    async def set_subtitle(self, index: int | None = None) -> bool:
        """Async Select subtitle.

        Parameters:
            index: int
                subtitle list reference
        Return:
            True if successful
        """
        if index is None: 
            indexes = {t.get("index"): t.get("title") for t in await self.get_subtitle_list()}
            index = self._next_data(indexes, self._current_subtitle)


        response = await self._req_json(f"{ZidooEndpoints.VIDEO_SET_SUBTITLE}?index={index}", log_errors=False)
        if response is not None and response.get("status") == 200:
            self._current_subtitle = index
            return True
        return False

    async def get_audio_list(self, log_errors=True) -> list:
        """Async Get audio track list.

        Returns:
            dictionary
                list of audio tracks
        """
        response = await self._req_json(ZidooEndpoints.VIDEO_AUDIO_LIST, log_errors=log_errors)
        if response is not None and response.get("status") == 200:
            self._audio_tracks = response.get("subtitles", [])
            return self._audio_tracks
        return []

    async def set_audio(self, index: int | None = None) -> bool:
        """Async Select audio track.

        Parameters
            index: int
                audio track list reference
        Return
            True if successful
        """
        if index is None: 
            indexes = {t.get("index"): t.get("title") for t in await self.get_audio_list()}
            index = self._next_data(indexes, self._current_audio)

            
        response = await self._req_json(f"{ZidooEndpoints.VIDEO_SET_AUDIO}?index={index}", log_errors=False)
        if response is not None and response.get("status") == 200:
            self._current_audio = index
            return True
        return False

    async def get_zoom_list(self) -> dict:
        """Async get video zoom list.

        Returns:
            dictionary
                list of zoom types
        """
        return_values = {}
        response = await self._req_json(ZidooEndpoints.VIDEO_ZOOM_LIST)
        if response is not None and response.get("status") == 200:
            for result in response["zoom"]:
                return_values[result.get("index")] = result.get("title")
        return return_values

    async def set_zoom(self, index: str | int | None = None) -> bool:
        """Async select video zoom.

        Parameters
            index: mode string or list index
                audio track list reference
        Return
            True if successful
        """
        zoom_list = await self.get_zoom_list()
        if isinstance(index, str):
            index_list = list(zoom_list.values())
            index = (
                index_list.index(index) if index in index_list else self._current_zoom
            )
        if index is None:
            index = self._next_data(zoom_list, self._current_zoom)
        response = await self._req_json(f"{ZidooEndpoints.VIDEO_SET_ZOOM}?index={index}", log_errors=False)
        if response is not None and response.get("status") == 200:
            self._current_zoom = index
            return True
        return False

    async def get_system_info(self, log_errors=True):
        """Async Get system information.

        Returns:
            json is successful:
                'status': 200
                'model': model name
                'ip': ip address
                'net_mac': wired mac address
                'wif_mac': wifi mac address
                'language': system language
                'firmware': firmware version
                'androidversion': os version
                'flash': flash/emmc memory size
                'ram':' ram memory size
                'ableRemoteSleep': network sleep compatible (buggy on Z9S)
                'ableRemoteReboot': network reboot compatible
                'ableRemoteShutdown': network shut down compatible
                'ableRemoteBoot': network boot compatible (wol)
                'pyapiversion': python api version
        """
        response = await self._req_json(ZidooEndpoints.GET_MODEL, log_errors=log_errors, max_retries=0)
        if response and response.get("status") == 200:
            response["pyapiversion"] = VERSION
            return response
        return None

    async def get_power_status(self) -> str:
        """Async Get power status.

        Returns:
            "on" when player is on
            "off" when player is not available
        """
        self._power_status = False
        try:
            response = await self.get_system_info()

            if response and response.get("status") == 200:
                self._power_status = True

        except:  # pylint: disable=broad-except
            pass

        if self._power_status is True:
            return "on"
        return "off"

    # TODO: investigate analogue volume control on eversolo devices
    # async def get_volume_info(self):
    #    """Async Get volume info. Not currently supported.
    #         volume_data = music_state.get("volumeData", {})
    #   current_volume = volume_data.get("currenttVolume")
    #   max_volume = volume_data.get("maxVolume")

    # async def set_volume_level(self, volume):
    #    """Async Set volume level. Not currently supported."""
    # max_volume = music_state.get("volumeData", {}).get("maxVolume", 100)
    # api_volume = int((volume / 100) * max_volume)
    # f"/ZidooMusicControl/v2/setDevicesVolume?volume={device_volume}"
    #    return 0

    async def get_audio_output(self) -> int:
        """Async Return last known audio output using API V2."""
        response = await self._req_json(ZidooEndpoints.MUSIC_IO_LIST, log_errors=False, timeout=TIMEOUT_INFO)
        if response is not None and response.get("status") == 200:
            # update the output list (since we have it)
            output_list = {}
            for result in response["outputData"]:
                if result.get("enable"):
                    name = result.get("name")
                    output_list[name] = result.get("tag")
            self._audio_output_list = output_list

            # return the index
            return response.get("outputIndex")

        # for debugging
        # output_list = {}
        # output_list["Output1"] = 0
        # output_list["Output2"] = 1
        # output_list["Output3"] = 3
        # self._audio_output_list = output_list
        return 0  # -1

    async def load_audio_output_list(self) -> dict:
        """Async Return audio output list."""
        return self._audio_output_list

    async def set_audio_output(self, output: str, log_errors=True) -> bool:
        """Async Set an audio output by audio output tag."""
        output_tag = self._audio_output_list[output]
        response = await self._req_json(f"{ZidooEndpoints.MUSIC_SET_IO}?tag={output_tag}")
        if response is not None and response.get("status") == 200:
            return True
        return False

    async def get_app_list(self, log_errors=True) -> dict:
        """Async Get the list of installed apps.

        Results
            list of openable apps
                <app name>: <app_id>
        """
        return_values = {}
        response = await self._req_json(ZidooEndpoints.GET_APPS, log_errors=log_errors)
        if response is not None and response.get("status") == 200:
            for result in response["apps"]:
                if result.get("isCanOpen"):
                    name = result.get("label")
                    return_values[name] = result.get("packageName")

        return return_values

    async def start_app(self, app_name: str, log_errors=True) -> bool:
        """Async Start an app by name.

        Parameters
            app_name: str
                app list reference
        Return
            True if successful
        """
        if len(self._app_list) == 0:
            self._app_list = await self.get_app_list(log_errors)
        if app_name in self._app_list:
            return await self._start_app(
                self._app_list[app_name], log_errors=log_errors
            )
        return False

    async def _start_app(self, app_id, log_errors=True) -> bool:
        """Async Start an app by package name."""
        response = await self._req_json(f"{ZidooEndpoints.OPEN_APP}?packageName={app_id}")
        if response is not None and response.get("status") == 200:
            return True
        return False

    async def get_device_list(self):
        """Async Return list of root file system devices.

        Returns:
            json device list if successful
                'name': device name
                'path': device path
                'type': device type (see ZDEVICE_TYPE)
        """
        response = await self._req_json(ZidooEndpoints.GET_DEVICES)
        if response is not None and response.get("status") == 200:
            return response["devices"]
        return None

    async def get_movie_list(
        self, filter_type: int = -1, max_count: int = DEFAULT_COUNT
    ):
        """Async Return list of movies.

        Parameters
            max_count: int
                maximum number of list items
            filter_type: int or str
                see ZVIDEO_FILTER_TYPE
        Returns
            json
                raw API response if successful
        """

        def byId(e):
            return e["id"]

        if filter_type in ZVIDEO_FILTER_TYPES:
            filter_type = ZVIDEO_FILTER_TYPES[filter_type]

        return await self._req_json(f"{ZidooEndpoints.POSTER_AGGREGATIONS}?start=0&count={max_count}&type={filter_type}")

    async def get_collection_list(self, movie_id: int | str):
        """Async Return video collection details.

        Parameters
            movie_id: int
                database movie_id
        Returns
            json
                raw API response if successful
        """
        return await self._req_json(f"{ZidooEndpoints.POSTER_COLLECTION}?id={movie_id}")

    async def get_movie_details(self, movie_id: int | str):
        """Async Return video details.

        Parameters
            movie_id: int
                database movie_id
        Returns
            json
                raw API response (no status)
        """
        return await self._req_json(f"{ZidooEndpoints.POSTER_DETAIL}?id={movie_id}")

    async def get_episode_list(self, season_id: int | str):
        """Async Return video list sorted by episodes.

        Parameters
            movie_id: int
                database movie_id
        Returns
            json:
                raw API episode list if successful
        """

        def byEpisode(e):
            return e["aggregation"]["episodeNumber"]

        response = await self.get_movie_details(season_id)

        if response is not None:
            episodes = response.get("aggregations")
            if episodes is None:
                # try alternative location
                result = response.get("aggregation")
                if result is not None:
                    episodes = result.get("aggregations")

            if episodes is not None:
                episodes.sort(key=byEpisode)
                return episodes
        return None

    async def _collection_video_id(self, movie_id: int) -> int:
        """Async Get collection id for movie."""
        response = await self.get_collection_list(movie_id)

        if response is not None:
            for result in response["data"]:
                if result["type"] == 0:
                    return result["aggregationId"]
        return movie_id

    async def get_music_list(
        self,
        music_type: int = 0,
        music_id: int | str | None = None,
        max_count: int = DEFAULT_COUNT,
    ):
        """Async Return list of music.

        Parameters
            max_count: int
                maximum number of list items
            filter_type: int or str
                see ZVIDEO_FILTER_TYPE
        Returns
            json
                raw API response if successful
        """
        if music_type == ZMEDIA_TYPE_ARTIST:
            return await self._get_artist_list(music_id, max_count)
        if music_type == ZMEDIA_TYPE_ALBUM:
            return await self._get_album_list(music_id, max_count)
        if music_type == ZMEDIA_TYPE_PLAYLIST:
            return await self._get_playlist_list(music_id, max_count)
        return await self._get_song_list(max_count)

    async def _get_song_list(self, max_count: int = DEFAULT_COUNT):
        """Async Return list of albums or album music.

        Parameters
            max_count: int
                maximum number of list items
        Returns
            json
                raw API response if successful
        """
        response = await self._req_json(f"{ZidooEndpoints.MUSIC_GET_SINGLE}?start=0&count={max_count}")
        if response:
            self._song_list = self._get_music_ids(response.get("array"))

        return response

    async def _get_album_list(
        self, album_id: int | str | None = None, max_count: int = DEFAULT_COUNT
    ):
        """Async Return list of albums or album music.

        Parameters
            album_id: int or str
                see ZVIDEO_FILTER_TYPE
            max_count: int
                maximum number of list items
        Returns
            json
                raw API response if successful
        """
        if album_id: return await self._req_json(f"{ZidooEndpoints.MUSIC_GET_ALBUM_MUSICS}?id={album_id}&start=0&count={max_count}")
        return await self._req_json(f"{ZidooEndpoints.MUSIC_GET_ALBUM}?start=0&count={max_count}")

    async def _get_artist_list(
        self, artist_id: int | str | None = None, max_count: int = DEFAULT_COUNT
    ):
        """Async Return list of artists or artist music.

        Parameters
            artist_id: int
                artist id
            max_count: int
                maximum number of list items
            filter_type: int or str
                see ZVIDEO_FILTER_TYPE
        Returns
            json
                raw API response if successful
        """
        if artist_id: return await self._req_json(f"{ZidooEndpoints.MUSIC_GET_ARTIST_MUSICS}?id={artist_id}&start=0&count={max_count}")
        return await self._req_json(f"{ZidooEndpoints.MUSIC_GET_ARTISTS}?start=0&count={max_count}")

    async def _get_playlist_list(self, playlist_id=None, max_count=DEFAULT_COUNT):
        """Async Return list of playlists.

        Parameters
            max_count: int
                maximum number of list items
            filter_type: int or str
                see ZVIDEO_FILTER_TYPE
        Returns
            json
                raw API response if successful
        """
        if playlist_id:
            if playlist_id == ZMEDIA_PLAYLIST[1]:
                response = await self._req_json(f"{ZidooEndpoints.MUSIC_GET_PLAY_QUEUE}?start=0&count={max_count}")
                if response: self._song_list = self._get_music_ids(response.get("array"))
            elif playlist_id == ZMEDIA_PLAYLIST[0]:
                response = await self._req_json(f"{ZidooEndpoints.MUSIC_GET_FAVORITES}?start=0&count={max_count}")
                if response: self._song_list = self._get_music_ids(response.get("array"))
            else:
                response = await self._req_json(f"{ZidooEndpoints.MUSIC_GET_SONGLIST_MUSICS}?id={playlist_id}&start=0&count={max_count}")
        else:
            response = await self._req_json(ZidooEndpoints.MUSIC_GET_SONGLISTS)
        return response

    async def search_movies(
        self, query: str, search_type: int = 0, max_count: int = DEFAULT_COUNT
    ):
        """Async Return list of video based on query.

        Parameters
            movie_id: int
                database movie_id
            search_type: int ot str
                see ZVIDEO_SEARCH_TYPES
        Returns
            json
                raw API response (no status)
        """
        if search_type in ZVIDEO_SEARCH_TYPES: search_type = ZVIDEO_SEARCH_TYPES[search_type]
        response = await self._req_json(f"{ZidooEndpoints.POSTER_SEARCH}?q={query}&type={search_type}&start=0&count={max_count}", timeout=TIMEOUT_SEARCH)
        if response is not None and response.get("status") == 200:
            return response
        return None

    async def search_music(
        self,
        query: str,
        search_type: int = 0,
        max_count: int = DEFAULT_COUNT,
        play: bool = False,
    ):
        """Async Return list of music based on query.

        Parameters
            query: str
                text to search
            search_type: int or str
                see ZMUSIC_SEARCH_TYPES
            max_count: int
                max number of songs returned
            play: bool
                automatically plays content.  search_type=0 only
        Returns
            json
                raw API response (no status)
        """
        if search_type in ZMUSIC_SEARCH_TYPES:
            search_type = ZMUSIC_SEARCH_TYPES[search_type]

        if search_type == 1:
            return await self._search_album(query, max_count)
        if search_type == 2:
            return await self._search_artist(query, max_count)
        response = await self._search_song(query, max_count)
        if response:
            self._song_list = self._get_music_ids(response.get("array"), sub="result")
            if play and self._song_list:
                await self.play_music(media_type="music", music_id=self._song_list[0])
        return response

    async def _search_song(self, query: str, max_count: int = DEFAULT_COUNT):
        """Async Search by song title.

        Parameters
            query: str
                text to search
        Returns
            json
                raw API response (no status)
        """
        return await self._req_json(f"{ZidooEndpoints.MUSIC_SEARCH}?key={query}&start=0&count={max_count}", timeout=TIMEOUT_SEARCH)

    async def _search_album(self, query: str, max_count: int = DEFAULT_COUNT):
        """Async Search by album name.

        Parameters
            query: str
                text to search
        Returns
            json
                raw API response (no status)
        """
        return await self._req_json(f"{ZidooEndpoints.MUSIC_SEARCH_ALBUM}?key={query}&start=0&count={max_count}", timeout=TIMEOUT_SEARCH)

    async def _search_artist(self, query: str, max_count: int = DEFAULT_COUNT):
        """Async Search by artist name.

        Parameters
            query: str
                text to search
        Returns
            json
                raw API response (no status)
        """
        return await self._req_json(f"{ZidooEndpoints.MUSIC_SEARCH_ARTIST}?key={query}&start=0&count={max_count}", timeout=TIMEOUT_SEARCH)

    async def play_file(self, uri: str) -> bool:
        """Async Play content by URI.

        Parameters
            uri: str
                path of file to play
        Returns
            True if successful
        """
        response = await self._req_json(f"{ZidooEndpoints.FILE_OPEN}?path={uri}&videoplaymode=0")
        if response and response.get("status") == 200:
            return True
        return False

    async def play_stream(self, uri: str, media_type) -> bool:
        """Async Play url by type.

        Uses undocumented v2 upnp FileOpen calls using 'res' and 'type'
            res: str
                quoted url
            type : int or str
                mime type or see ZTYPE_MIMETYPE
            other information parameters can be used
                name: str (title?)
                date: datetime
                resolution: <width>x<height>
                bitrate: int (audio?)
                size: int (duration?)
                channels: int (audio?)
                bitRates: int (audio?)
                way: {0,1,2,3} (play mode?)
                album: str
                number: int (audio)
                sampleRates: int (audio)
                albumArt: url (audio)
        Parameters:
            uri: str
                uri link to stream
            media_type: int
                See ZTYPE_MIMETYPE
        Returns
            True if successful
        """
        # take major form mime type
        if isinstance(media_type, str) and "/" in media_type:
            media_type = media_type.split("/")[0]

        if media_type in ZTYPE_MIMETYPE:
            media_type = ZTYPE_MIMETYPE[media_type]

        # the res uri needs to be double quoted to protect keys etc.
        # use safe='' in quote to force "/" quoting
        uri = urllib.parse.quote(uri, safe="")

        upnp = urllib.parse.quote(
            f"upnp://{ZUPNP_SERVERNAME}/{VERSION}?type={media_type}&res={uri}", safe=""
        )
        _LOGGER.debug("Stream command %s", str(upnp))

        response = await self._req_json(f"{ZidooEndpoints.FILE_OPEN_V2}?url={upnp}")
        if response and response.get("code") == 0:
            return True
        return False

    async def play_movie(self, movie_id: int | str, video_type: int | str = -1) -> bool:
        """Async Play video content by Movie id.

        Parameters
            movie_id
                database id
        Returns
            True if successful
        """
        # uses the agreggateid to find the first video to play
        if video_type != 0:
            movie_id = await self._collection_video_id(movie_id)
        response = await self._req_json(f"{ZidooEndpoints.POSTER_PLAY_VIDEO}?id={movie_id}&type={video_type}")
        if response and response.get("status") == 200:
            return True
        return False

    def _get_music_ids(self, data, key="id", sub=None):
        ids = []
        if data:
            for item in data:
                result = item.get(sub) if sub else item
                if result:
                    music_id = result.get(key)
                    ids.append(str(music_id))
        return ids

    async def play_music(
        self,
        media_id: int | str | None = None,
        media_type: int | str = "music",
        music_id: int | str | None = None,
    ) -> bool:
        """Async Play video content by id.

        Parameters:
            media_id
                database id for media type (or ids for music type)
            media_type
                see ZMUSIC_SEARCH_TYPE
            music_id
                database id for track to play (use None or -1 for first)

        Returns:
            True if successfull
        """
        if media_type in ZMUSIC_PLAYLISTTYPE and media_id not in ZMEDIA_PLAYLIST:
            response = await self._req_json(f"{ZidooEndpoints.MUSIC_PLAY_MUSIC}?type={ZMUSIC_PLAYLISTTYPE[media_type]}&id={media_id}&musicId={music_id}&music_type=0&trackIndex=1&sort=0")
        else: 
            response = await self._req_json(f"{ZidooEndpoints.MUSIC_PLAY_MUSICS}?ids={'%2C'.join(self._song_list)}&musicId={music_id}&trackIndex=-1")
        if response and response.get("status") == 200:
            return True
        return False

    async def get_video_playlist(self):
        """Async Return the current video playlist.

        Returns:
            json if successful
                'status': 200
                'size': count
                'playList' : array
                    'title': video name (file name)
                    'index': int
        """
        response = await self._req_json(ZidooEndpoints.VIDEO_PLAYLIST)
        if response and response.get("status") == 200:
            return response
        return None

    async def get_music_playlist(self, max_count: int = DEFAULT_COUNT):
        """Async Get current music player playlist.

        Parameters
            max_count: int
                list size limit
        Returns
            raw api response if successful
        """
        return await self._req_json(f"{ZidooEndpoints.MUSIC_GET_PLAY_QUEUE}?start=0&count={max_count}")

    async def get_file_list(self, uri: str, file_type: int = 0):
        """Async Return file list in hass format.

        Returns:
            json if successful
                'status':200
                'isExists':True
                'perentPath':'/storage/356d9775-8a40-4d4e-8ef9-9eea931fc5ae'
                'filelist': list
                    'name': file name
                    'type': file type
                    'path': full file path
                    'isBDMV': True if ?high definition
                    'isBluray': True if blue ray resolution
                    'length': length in ms
                    'modifyDate': linux date code
        """
        response = await self._req_json(f"{ZidooEndpoints.FILE_LIST}?path={uri}&type={file_type}")
        if response is not None and response.get("status") == 200:
            return response
        return {"filelist": []}

    async def get_host_list(self, uri: str, host_type: int = 1005):
        """Async Return host list of saved network shares.

        Returns:
            json if successful
                'status':200
                'filelist': list
                    'name': host/share name
                    'type': file type
                    'path': full file path
                    'isBDMV': True if ?high definition
                    'isBluray': True if blue ray resolution
                    'length': length in ms
                    'modifyDate': linux date code
        """
        response = await self._req_json(f"{ZidooEndpoints.FILE_HOST}?path={uri}&type={host_type}")
        _LOGGER.debug("zidoo host list: %s", str(response))

        return_value = {}
        share_list = []
        if response is not None and response.get("status") == 200:
            return_value["status"] = 200
            hosts = response["hosts"]
            for item in hosts:
                response_share = await self.get_file_list(item.get("ip"), item.get("type"))
                hostname = item.get("name").split("/")[-1]
                if response_share is not None and response_share.get("status") == 200:
                    for share in response_share["filelist"]:
                        share["name"] = hostname + "/" + share.get("name")
                        share_list.append(share)
        return_value["filelist"] = share_list
        return return_value

    def generate_image_url(
        self,
        media_id: int | str,
        media_type: int | str,
        width: int = 400,
        height: int | None = None,
    ) -> str:
        """Get link to thumbnail."""
        if media_type in ZVIDEO_SEARCH_TYPES:
            if height is None:
                height = width * 3 / 2
            return self._generate_movie_image_url(media_id, width, height)
        if media_type in ZMUSIC_SEARCH_TYPES:
            if height is None:
                height = width
            return self._generate_music_image_url(
                media_id, ZMUSIC_SEARCH_TYPES[media_type], width, height
            )
        return ""

    def _generate_movie_image_url(
        self, movie_id: int | str, width: int = 400, height: int = 600
    ) -> str:
        """Get link to thumbnail.

        Parameters
            movie_id: int
                database id
            width: int
                image width in pixels
            height: int
                image height in pixels
        Returns
            url for image
        """
        return f"http://{self._host}/{ZidooEndpoints.POSTER_GET_POSTER}?id={movie_id}&w={width}&h={height}"

    def _generate_music_image_url(
        self,
        music_id: int | str,
        music_type: int | str = 0,
        width: int = 200,
        height: int = 200,
    ) -> str:
        """Get link to thumbnail.

        Parameters
            music_id: int
                dtanabase id
            width: int
                image width in pixels
            height: int
                image height in pixels
        Returns
            url for image
        """
        return f"http://{self._host}/{ZidooEndpoints.MUSIC_GET_IMAGE}?id={music_id}&music_type={ZMUSIC_IMAGETYPE[music_type]}&type={music_type}&target={ZMUSIC_IMAGETARGET[music_type]}"

    def generate_current_image_url(
        self, width: int = 1080, height: int = 720
    ) -> str | None:
        """Get link to artwork.

        Parameters
            movie_id: int
                database id
            width: int
                image width in pixels
            height: int
                image height in pixels
        Returns
            url for image
        """
        url = None

        if self._current_source == ZCONTENT_VIDEO and self._video_id > 0:
            url = f"http://{self._host}/{ZidooEndpoints.POSTER_GET_BACKDROP}?id={self._video_id}&w={width}&h={height}"
        if self._current_source == ZCONTENT_MUSIC:
            if isinstance(self._music_id, str):
                url = self._music_id
            elif self._music_id > 0:
                url = f"http://{self._host}/{ZidooEndpoints.MUSIC_GET_IMAGE}?id={self._music_id}&music_type={self._music_type}&type=4&target=16"
        return url

    async def turn_on(self):
        """Async Turn the media player on."""
        # Try using the power on command incase the WOL doesn't work
        self._wakeonlan()
        return await self._send_key(ZKEY_POWER_ON, False)

    async def turn_off(self, standby=False):
        """Async Turn off media player."""
        return await self._send_key(ZKEY_POWER_STANDBY if standby else ZKEY_POWER_OFF)

    async def volume_up(self):
        """Async Volume up the media player."""
        return await self._send_key(ZKEY_VOLUME_UP)

    async def volume_down(self):
        """Async Volume down media player."""
        return await self._send_key(ZKEY_VOLUME_DOWN)

    async def mute_volume(self):
        """Async Send mute command."""
        return self._send_key(ZKEY_MUTE)

    async def media_play(self):
        """Async Send play command."""
        if self._current_source == ZCONTENT_NONE and self._last_video_path:
            return await self.play_file(self._last_video_path)
        if self._current_source == ZCONTENT_MUSIC:
            return await self._req_json(ZidooEndpoints.MUSIC_PLAY_PAUSE)
        # Adding native play/pause endpoint
        if self._current_source == ZCONTENT_VIDEO:
            # status=1 for Play
            response = await self._req_json(f"{ZidooEndpoints.VIDEO_CHANGE_STATUS}?status=1")
            return True if response and response.get("status") == 200 else False
        return await self._send_key(ZKEY_MEDIA_PLAY)

    async def media_pause(self):
        """Async Send media pause command to media player."""
        if self._current_source == ZCONTENT_MUSIC:
            return await self._req_json(ZidooEndpoints.MUSIC_PLAY_PAUSE)
        # Adding native play/pause endpoint
        if self._current_source == ZCONTENT_VIDEO:
            # status=0 for Pause
            response = await self._req_json(f"{ZidooEndpoints.VIDEO_CHANGE_STATUS}?status=0")
            return True if response and response.get("status") == 200 else False
        return await self._send_key(ZKEY_MEDIA_PAUSE)

    async def media_stop(self):
        """Async Send media pause command to media player."""
        return await self._send_key(ZKEY_MEDIA_STOP)

    async def media_next_track(self):
        """Async Send next track command."""
        if self._current_source == ZCONTENT_MUSIC:
            return await self._req_json(ZidooEndpoints.MUSIC_PLAY_NEXT)
        # Adding native next-video endpoint
        if self._current_source == ZCONTENT_VIDEO:
            # type=0 (playlist), tag=1 (next)
            response = await self._req_json(f"{ZidooEndpoints.VIDEO_CHANGE_VIDEO}?type=0&tag=1")
            return True if response and response.get("status") == 200 else False
        return await self._send_key(ZKEY_MEDIA_NEXT)

    async def media_previous_track(self):
        """Async Send the previous track command."""
        if self._current_source == ZCONTENT_MUSIC:
            return await self._req_json(ZidooEndpoints.MUSIC_PLAY_LAST)
        # Adding native prev-video endpoint
        if self._current_source == ZCONTENT_VIDEO:
            # type=0 (playlist), tag=0 (previous)
            response = await self._req_json(f"{ZidooEndpoints.VIDEO_CHANGE_VIDEO}?type=0&tag=0")
            return True if response and response.get("status") == 200 else False
        return self._send_key(ZKEY_MEDIA_PREVIOUS)

    async def media_next_chapter(self):
        """Async Skip to next chapter in video natively."""
        if self._current_source == ZCONTENT_VIDEO:
            # type=1 (chapter), tag=1 (next)
            response = await self._req_json(f"{ZidooEndpoints.VIDEO_CHANGE_VIDEO}?type=1&tag=1")
            return True if response and response.get("status") == 200 else False
        return False

    async def media_previous_chapter(self):
        """Async Skip to previous chapter in video natively."""
        if self._current_source == ZCONTENT_VIDEO:
            # type=1 (chapter), tag=0 (previous)
            response = await self._req_json(f"{ZidooEndpoints.VIDEO_CHANGE_VIDEO}?type=1&tag=0")
            return True if response and response.get("status") == 200 else False
        return False

    async def set_media_position(self, position):
        """Async Set the current playing position.

        Parameters
            position
                position in ms
        Return
            True if successful
        """
        if self._current_source == ZCONTENT_VIDEO:
            response = await self._set_movie_position(position)
        elif self._current_source == ZCONTENT_MUSIC:
            response = await self._set_audio_position(position)

        if response is not None:
            return True
        return False

    async def _set_movie_position(self, position):
        """Async Set current position for video player."""
        response = await self._req_json(f"{ZidooEndpoints.VIDEO_SEEK}?positon={int(position)}")
        if response is not None and response.get("status") == 200:
            return response
        return None

    async def _set_audio_position(self, position):
        """Async Set current position for music player."""
        response = await self._req_json(f"{ZidooEndpoints.MUSIC_SEEK}?time={int(position)}")
        if response is not None and response.get("status") == 200:
            return response
        return None
