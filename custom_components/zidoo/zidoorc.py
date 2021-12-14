"""
Zidoo Remote Control API
By Wizmo
  Based on the Sony BraviaRC BY Antonio Parraga Navarro
"""
import logging
import json
import socket
import struct
import requests
from datetime import datetime
import time
import urllib.parse

_LOGGER = logging.getLogger(__name__)

TIMEOUT = 2             # default timeout
CONF_PORT = 9529        # default api port

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
ZKEY_MEDIA_STOP = "Key.MediaStop"
ZKEY_MEDIA_PAUSE = "Key.MediaPause"
ZKEY_MEDIA_NEXT = "Key.MediaNext"
ZKEY_MEDIA_PREVIOUS = "Key.MediaPrev"
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
ZKEY_MEDIA_BACKWARDS = "Key.MediaBackward"
ZKEY_MEDIA_FORWARDS = "Key.MediaForward"
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

"""Movie Player entry types"""
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
    ZTYPE_OTHER: "other"
}

ZCONTENT_VIDEO = 'Video Player'
ZCONTENT_MUSIC = 'Music Player'
ZCONTENT_NONE = ''

"""Movie Player search keys"""
ZVIDEO_FILTER_TYPES = {
    "all": 0,
    "favorite": 1,
    "recent": 2,
    "movie": 3,
    "tvshow": 4,
    "sd": 5,
    "bluray": 6,
    "4k": 7,
    "filter8": 8,
    "unlocked": 9,
    "filter10": 10,
    "unwatched": 11,
    "unmatched": 12,
}
class ZidooRC(object):
    def __init__(self, host, psk=None, mac=None):
        """Initialize the Zidoo class.
        Parameters
            mac:
                address is optional and can be used to manually assign the WOL address.
            psk:
                authorization passwortd key.  If not assigned, standard basic auth is used.
        """

        self._host = "{}:{}".format(host, CONF_PORT)
        self._mac = mac
        self._psk = psk
        self._cookies = None
        self._commands = []
        self._content_mapping = []
        self._current_source = None
        self._app_list = {}
        self._power_status = False
        self._video_id = -1
        self._music_id = -1
        self._last_video_path = None
        self._movie_info = {}

    def _jdata_build(self, method, params=None):
        if params:
            ret = json.dumps(
                {"method": method, "params": [params], "id": 1, "version": "1.0"}
            )
        else:
            ret = json.dumps(
                {"method": method, "params": [], "id": 1, "version": "1.0"}
            )
        return ret

    def connect(self, clientid="client", nickname="Client"):
        """Connect to player and get authentication cookie.
        Parameters
            clientid: str
                id assigned to connection.
            nickname: str
                name assigned to connection.
        Returns
            json
                raw api response if sucessful.
        """
        authorization = json.dumps(
            {
                "method": "actRegister",
                "params": [
                    {"clientid": clientid, "nickname": nickname, "level": "private"},
                    [{"value": "yes", "function": "WOL"}],
                ],
                "id": 1,
                "version": "1.0",
            }
        ).encode("utf-8")

        headers = {"Connection": "keep-alive"}

        auth = None

        # if pin:
        #    auth = ('', pin)

        url = "http://{}/ZidooControlCenter/getModel".format(self._host)
        try:
            response = requests.post(
                url, data=authorization, headers=headers, timeout=TIMEOUT, auth=auth
            )
            response.raise_for_status()

        except requests.exceptions.Timeout as exception_instance:
            _LOGGER.info("[I] Timeout occurred: " + str(exception_instance))
            return None

        except requests.exceptions.ConnectTimeout as exception_instance:
            _LOGGER.info("[I] ConnectTimeout occurred: " + str(exception_instance))
            return None

        except requests.exceptions.HTTPError as exception_instance:
            _LOGGER.warning("[W] HTTPError: " + str(exception_instance))
            return None

        except Exception as exception_instance:  # pylint: disable=broad-except
            _LOGGER.error("[W] Exception: " + str(exception_instance))
            return None

        else:
            resp = response.json()
            _LOGGER.debug(json.dumps(resp, indent=4))
            if resp is not None or resp.get("status") == 200:
                self._cookies = response.cookies
                _LOGGER.debug("cookie: " + str(response.cookies))
                if self._mac is None:
                    self._mac = resp.get("net_mac")
                self._power_status = True
                return resp

    def _recreate_auth_cookie(self):
        cookies = requests.cookies.RequestsCookieJar()
        cookies.set("auth", self._cookies.get("auth"))
        return cookies

    def is_connected(self):
        """Basic check for connection status.
        Returns
            bool
                True if connected.
        """
        if self._cookies is None:
            return False
        else:
            return True

    def _wakeonlan(self):
        """Sends WOL command to known mac addresses."""
        if self._mac is not None:
            addr_byte = self._mac.split(":")
            hw_addr = struct.pack(
                "BBBBBB",
                int(addr_byte[0], 16),
                int(addr_byte[1], 16),
                int(addr_byte[2], 16),
                int(addr_byte[3], 16),
                int(addr_byte[4], 16),
                int(addr_byte[5], 16),
            )
            msg = b"\xff" * 6 + hw_addr * 16
            socket_instance = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            socket_instance.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            socket_instance.sendto(msg, ("<broadcast>", 9))
            socket_instance.close()

    def _send_key(self, key, log_error=False):
        """Sends Remote Control button command to device.
        Parameters
            key: str
                remote control key command (see ZKEY list)
            log_error: bool
                suppesses error logging if False
        Returns
            True if sucessful
        """
        url = "ZidooControlCenter/RemoteControl/sendkey"
        params = {"key": key}

        response = self._req_json(url, params, log_error)

        if response and response.get("status") == 200:
            return True
        return False


    def _req_json(self, url, params={}, log_errors=True):
        """Send request command via HTTP json to player.
        Parameters
            url: str
                api call.
            params: str
                api parameters.
            log_error: bool
                suppesses error logging if False
        Returns
            json
                raw API response
        """
        headers = {}
        if self._psk is not None:
            headers["X-Auth-PSK"] = self._psk

        url = "http://{}/{}".format(self._host, url)

        try:
            # self._cookies = self._recreate_auth_cookie()
            response = requests.get(
                url, params, cookies=self._cookies, timeout=TIMEOUT, headers=headers
            )

        except requests.exceptions.Timeout as exception_instance:
            if log_errors and self._power_status:
                _LOGGER.info("[I] Timeout occurred: " + str(exception_instance))

        except requests.exceptions.ConnectTimeout as exception_instance:
            if log_errors and self._power_status:
                _LOGGER.info("[I] ConnectTimeout occurred: " + str(exception_instance))

        except requests.exceptions.ConnectionError as exception_instance:
            if log_errors and self._power_status:
                _LOGGER.info("[I] Connect occurred: " + str(exception_instance))

        except requests.exceptions.HTTPError as exception_instance:
            if log_errors:
                _LOGGER.warning("HTTPError: " + str(exception_instance))

        except Exception as exception_instance:  # pylint: disable=broad-except
            if log_errors:
                _LOGGER.error("Exception: " + str(exception_instance))

        else:
            result = json.loads(response.content.decode("utf-8"))
            return result

    def play_content(self, uri):
        """Play content by URI.
        Parameters
            uri: str
                path of file to play.
        Returns
            True if sucessful
        """
        url = "ZidooFileControl/openFile?path={}&videoplaymode={}".format(uri, 0)

        response = self._req_json(url)

        if response and response.get("status") == 200:
            return True
        return False

    def get_source(self, source):
        """Returns last known app"""
        return self._current_source

    def load_source_list(self):
        """Returns app list."""
        return self.get_app_list()

    def get_playing_info(self):
        """Gets playing information of active app.
        Returns
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
                date: release date (movie only)
                episode: episode number (tv only)
                episode_name: episode title (tv only)
                season: season number (tv only)
                season_name: season title (tv only)
                series_name: series title (tv only)
        """
        return_value = {}

        response = self._get_video_playing_info()
        if response is not None:
            return_value = response
            return_value["source"] = "video"
            if return_value.get("status") == True:
                self._current_source = ZCONTENT_VIDEO
                return {**return_value,**self._movie_info}

        response = self._get_music_playing_info()
        if response is not None:
            return_value = response
            return_value["source"] = "music"
            if return_value["status"] == True:
                self._current_source = ZCONTENT_MUSIC
                return return_value

        return return_value

    def _get_video_playing_info(self):
        """Get information from built in video player."""
        return_value = {}
        response = self._req_json("ZidooVideoPlay/getPlayStatus")

        # _LOGGER.debug(json.dumps(response, indent=4))
        if response is not None and response.get("status") == 200:
            if response.get("video"):
                result = response.get("video")
                return_value["status"] = (result.get("status")==1)
                return_value["title"] = result.get("title")
                return_value["uri"] = result.get("path")
                return_value["duration"] = result.get("duration")
                return_value["position"] = result.get("currentPosition")
                if return_value["status"] is True and return_value["uri"] != self._last_video_path:
                    self._last_video_path = return_value["uri"]
                    self._video_id = self._get_id_from_uri(self._last_video_path)
                return return_value
        return None

    def _get_id_from_uri(self, uri):
        """returns the movie id from the path"""
        movie_id = 0
        movie_info = {}

        response = self._req_json(
            "ZidooPoster/v2/getAggregationOfFile?path={}".format(
                urllib.parse.quote(uri)
            )
        )

        if response: # and response.get("status") == 200:
            result = response.get("video")
            if result is not None:
                movie_id = result.get("parentId")
            movie_info["type"] = response.get("type")
            result = response.get("movie")
            if result is not None:
                movie_info["movie_name"] = result.get("name")
                movie_info["tag"] = result["aggregation"].get("tagLine")
                #movie_info["date"] = result["aggregation"].get("releaseDate").split('-')[0]
                movie_info["date"] = datetime.strptime(result["aggregation"].get("releaseDate"), "%Y-%m-%d")
            result = response.get("episode")
            if result is not None:
                movie_info["episode"] =  result["aggregation"].get("episodeNumber")
                movie_info["episode_name"] =  result["aggregation"].get("name")
            result = response.get("season")
            if result is not None:
                movie_info["season"] = result["aggregation"].get("seasonNumber")
                movie_info["season_name"] = result["aggregation"].get("name")
                movie_info["series_name"] = result["aggregation"].get("tvName")

            self._movie_info = movie_info

        _LOGGER.debug("new media detected: uri-'{}' dbid={}".format(uri, movie_id))
        return movie_id

    def _get_music_playing_info(self):
        """Get information from built in Music Player"""
        return_value = {}
        response = self._req_json("ZidooMusicControl/getPlayStatus")

        # _LOGGER.debug(json.dumps(response, indent=4))
        if response is not None and response.get("status") == 200:
            return_value["status"] = response.get("isPlay")
            result = response.get("music")
            if result is not None:
                return_value["title"] = result.get("title")
                return_value["artist"] = result.get("artist")
                return_value["track"] = result.get("number")
                return_value["uri"] = result.get("uri")
                self._music_id = result.get("databaseId")

                result = response.get("state")
                return_value["duration"] = result.get("duration")
                return_value["position"] = result.get("position")

                result = response.get("state")
                if result is not None:
                    # update with satte - playing for newer firmware
                    return_value["status"] = result.get("playing")

                return return_value
        return None

    def _get_movie_playing_info(self):
        """Get information from built in Movie Player."""
        return_value = {}

        response = self._req_json("ZidooControlCenter/getPlayStatus")

        if response is not None and response.get("status") == 200:
            if response.get("file"):
                result = response.get("file")
                return_value["status"] = (result.get("status")==1)
                return_value["title"] = result.get("title")
                return_value["uri"] = result.get("path")
                return_value["duration"] = result.get("duration")
                return_value["position"] = result.get("currentPosition")
                return return_value
        return None

    def get_play_modes(self):
        """Get the playmode list
        Returns
            json
                raw api response when successful
        """
        response = self._req_json("ZidooVideoPlay/getPlayModeList")

        if response is not None and response.get("status") == 200:
            return response

    def get_system_info(self):
        """Get system information
        Returns
            json is successful
                'status': 200
                'model':model name
                'ip': ip address
                'net_mac':lan mac address
                'wif_mac': wifi mac address
                'language': 'en'
                'firmware': firmwate version
                'androidversion': os version
                'flash': flash memory size
                'ram':' ram memory size
                'ableRemoteSleep':True (buggy on Z9S)
                'ableRemoteReboot':True
                'ableRemoteShutdown':True
                'ableRemoteBoot':False
        """
        response = self._req_json("ZidooControlCenter/getModel")

        if response is not None and response.get("status") == 200:
            return response

    def get_power_status(self):
        """Get power status
        Returns
            "on" when player is on
            "off" when player is not availblessful
        """
        self._power_status = False
        try:
            response = self.get_system_info()

            if response is not None:
                self._power_status = True

        except:  # pylint: disable=broad-except
            pass

        if self._power_status is True:
            return "on"
        return "off"

    def get_volume_info(self):
        """Get volume info. Not currently supported."""
        return None

    def set_volume_level(self, volume):
        """Set volume level. Not currently supported."""
        # api_volume = str(int(round(volume * 100)))
        return 0

    def get_app_list(self, log_errors=True):
        """Get the list of installed apps
        Parameters
            log_errors
                set to "False" to disbale errors
        Results
            list
                <app name>: <app_id>
        """
        return_values = {}

        response = self._req_json("ZidooControlCenter/Apps/getApps")

        if response is not None and response.get("status") == 200:
            for result in response["apps"]:
                if result.get("isCanOpen"):
                    name = result.get("label")
                    return_values[name] = result.get("packageName")

        return return_values

    def start_app(self, app_name, log_errors=True):
        """Start an app by name
        Parameters
            app_name: str
                app list reference
        Return
            True if sucessful
        """
        if len(self._app_list) == 0:
            self._app_list = self.get_app_list(log_errors)
        if app_name in self._app_list:
            return self._start_app(self._app_list[app_name], log_errors=log_errors)
        return False

    def _start_app(self, app_id, log_errors=True):
        """Start an app by package name"""
        response = self._req_json(
            "ZidooControlCenter/Apps/openApp?packageName={}".format(app_id)
        )

        if response is not None and response.get("status") == 200:
            return True
        return False

    def get_device_list(self):
        """Return list of root file system devices.
        Returns
            json device list if sucessful
                'name': device name
                'path': device path
                'type': device type (see ZDECIVE_TYPE)
        """
        response = self._req_json("ZidooFileControl/getDevices")

        if response is not None and response.get("status") == 200:
            return response["devices"]

    def get_movie_list(self, page_limit=250, video_type=-1):
        """Return list of movies
        Parameters
            page_limit: str
                maxumum number of list items
            video_type: int
                see ZVIDEO_FILTEER_TYPE
        Returns
            json
                raw API response if successful
        """
        if video_type in ZVIDEO_FILTER_TYPES:
            video_type = ZVIDEO_FILTER_TYPES[video_type]

        response = self._req_json(
            "ZidooPoster/getVideoList?page=1&pagesize={}&type={}".format(
                page_limit, video_type
            )
        )

        if response is not None and response.get("status") == 200:
            return response

    def get_collection_list(self, movie_id):
        """Return video collection details
        Parameters
            movie_id: int
                database movie_id
        Returns
            json
                raw API response if successful
        """
        response = self._req_json("ZidooPoster/getCollection?id={}".format(movie_id))

        if response is not None and response.get("status") == 200:
            return response

    def get_movie_details(self, movie_id):
        """Return video details
        Parameters
            movie_id: int
                database movie_id
        Returns
            json
                raw API response (no status)
        """
        #response = self._req_json("ZidooPoster/getDetail?id={}".format(movie_id))
        response = self._req_json("Poster/v2/getDetail?id={}".format(movie_id))

        if response is not None:# and response.get("status") == 200:
            return response

    def get_episode_list(self, season_id):
        """Returns list video list sorted by episodes
        Parameters
            movie_id: int
                database movie_id
        Returns
            json:
                raw API episode list if successful
        """

        def byEpisode(e):
            return e['aggregation']['episodeNumber']

        response = self.get_movie_details(season_id)

        if response is not None:
            episodes = response.get('aggregations')
            if episodes is None:
				# try alternative location
                result = response.get('aggregation')
                if result is not None:
                    episodes = result.get('aggregations')

            if episodes is not None:
                episodes.sort(key=byEpisode)
                return episodes

    def _collection_video_id(self, movie_id):
        response = self.get_collection_list(movie_id)

        if response is not None:
            for result in response["data"]:
                return result["aggregationId"]

    def play_movie(self, movie_id, video_type=0):
        """Play video content by Movie id.
        Parameters
            movie_id
                database id
        Returns
            True if sucessfuL
        """
        # uses the agreggateid to find the first video to play
        video_id = self._collection_video_id(movie_id)
        # print("Video id : {}".format(video_id))

        response = self._req_json(
            "ZidooPoster/PlayVideo?id={}&type={}".format(video_id, video_type)
        )

        if response and response.get("status") == 200:
            return True
        return False

    def generate_movie_image_url(self, movie_id, width=100, height=150):
        """Get link to thumbnail
        Parameters
            movie_id: int
                dtanabase id
            width: int
                image width in pixels
            height: int
                image height in pixels
        Returns
            url for image
        """
        url = "http://{}/ZidooPoster/getFile/getPoster?id={}&w={}&h={}".format(
            self._host, movie_id, width, height
        )

        return url

    def generate_current_image_url(self, width=1080, height=720):
        """Gets link to artwork
        Parameters
            movie_id: int
                dtanabase id
            width: int
                image width in pixels
            height: int
                image height in pixels
        Returns
            url for image
            """
        url = None

        if self._current_source == ZCONTENT_VIDEO and self._video_id > 0:
            url = "http://{}/ZidooPoster/getFile/getBackdrop?id={}&w={}&h={}".format(
                self._host, self._video_id, width, height
            )

        if self._current_source == ZCONTENT_MUSIC and self._music_id > 0:
            url = "http://{}/ZidooMusicControl/v2/getImage?id={}&musicType=1&type=4&target=16".format(
                self._host, self._music_id
            )

        #_LOGGER.debug("zidoo getting current image: url-{}".format(url))
        return url

    def get_file_list(self, uri, file_type=0):
        """get file list in hass format
        Returns
            json if sucessful
                'status':200
                'isExists':True
                'perentPath':'/storage/356d9775-8a40-4d4e-8ef9-9eea931fc5ae'
                'filelist': list
                    'name': file name
                    'type': file type
                    'path': full file path
                    'isBDMV': True is high definition
                    'isBluray': True is blue ray resolution
                    'length': length in ms
                    'modifyDate': linux date code
        """
        response = self._req_json(
            "ZidooFileControl/getFileList?path={}&type={}".format(uri, file_type)
        )

        if response is not None and response.get("status") == 200:
            return response

    def select_source(self, source):
        """Set the input source.
        Parameters
            source:  content
        Return
            True if sucessful
        """
        if len(self._content_mapping) == 0:
            self._content_mapping = self.load_source_list()

        if source in self._content_mapping:
            uri = self._content_mapping[source]
            return self.play_content(uri)
        return False

    def turn_on(self):
        """Turn the media player on."""
        self._wakeonlan()
        # Try using the power on command incase the WOL doesn't work
        if self.get_power_status() != "active":
            self._send_key(ZKEY_POWER_ON)

    def turn_off(self):
        """Turn off media player."""
        self._send_key(ZKEY_POWER_OFF)

    def volume_up(self):
        """Volume up the media player."""
        self._send_key(ZKEY_VOLUME_UP)

    def volume_down(self):
        """Volume down media player."""
        self._send_key(ZKEY_VOLUME_DOWN)

    def mute_volume(self):
        """Send mute command."""
        self._send_key(ZKEY_MUTE)

    def media_play(self):
        """Send play command."""
        # self._send_key(ZKEY_OK)
        self._send_key(ZKEY_MEDIA_PLAY)

    def media_pause(self):
        """Send media pause command to media player."""
        self._send_key(ZKEY_MEDIA_PAUSE)

    def media_stop(self):
        """Send media pause command to media player."""
        self._send_key(ZKEY_MEDIA_STOP)

    def media_next_track(self):
        """Send next track command."""
        self._send_key(ZKEY_MEDIA_NEXT)

    def media_previous_track(self):
        """Send the previous track command."""
        self._send_key(ZKEY_MEDIA_PREVIOUS)

    def calc_time(self, *times):
        """Calculate total playimg time
        Parameters
            times
                list of durations
        Return
            sum of times, value is returned in HH:MM."""
        total_secs = 0
        for tms in times:
            time_parts = [int(s) for s in tms.split(":")]
            total_secs += (time_parts[0] * 60 + time_parts[1]) * 60 + time_parts[2]
        total_secs, sec = divmod(total_secs, 60)
        hour, minute = divmod(total_secs, 60)
        if hour >= 24:  # set 24:10 to 00:10
            hour -= 24
        return "%02d:%02d" % (hour, minute)

    def playing_time(self, startdatetime, durationsec):
        """Calculates playing time
        Parameters
            Give starttime, endtime and percentage played.
            Start time format: 2017-03-24T00:00:00+0100
            Using that, we calculate number of seconds to end time.
        """

        date_format = "%Y-%m-%dT%H:%M:%S"
        now = datetime.now()
        stripped_tz = startdatetime[:-5]
        start_date_time = datetime.strptime(stripped_tz, date_format)
        start_time = time.strptime(stripped_tz, date_format)

        try:
            playingtime = now - start_date_time
        except TypeError:
            playingtime = now - datetime(*start_time[0:6])

        try:
            starttime = datetime.time(start_date_time)
        except TypeError:
            starttime = datetime.time(datetime(*start_time[0:6]))

        duration = time.strftime("%H:%M:%S", time.gmtime(durationsec))
        endtime = self.calc_time(str(starttime), str(duration))
        starttime = starttime.strftime("%H:%M")
        perc_playingtime = int(round(((playingtime.seconds / durationsec) * 100), 0))

        return_value = {}

        return_value["start_time"] = starttime
        return_value["end_time"] = endtime
        return_value["media_position"] = playingtime.seconds
        return_value["media_position_perc"] = perc_playingtime

        return return_value

    def set_media_position(self, position, durationsec=1):
        """Set the current playing position.
        Parameters
            position
                position in ms
        Return
            True if sucessful
        """
        response = self._set_movie_position(position)
        if response is None:
            response = self._set_audio_position(position)

        if response is not None:
            return True
        return False

    def _set_movie_position(self, position):
        """Set current posotion for video player"""
        response = self._req_json(
            "ZidooVideoPlay/seekTo?positon={}".format(int(position))
        )

        if response is not None and response.get("status") == 200:
            return response

    def _set_audio_position(self, position):
        """Set current position for music player"""
        response = self._req_json(
            "ZidooMusicControl/seekTo?time={}".format(int(position))
        )

        if response is not None and response.get("status") == 200:
            return response
