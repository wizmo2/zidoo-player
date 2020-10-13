"""
Sony Zidoo RC API
By Antonio Parraga Navarro
dedicated to Isabel
"""
import logging
import collections
import json
import socket
import struct
import requests
from datetime import datetime
import time
import sys
from xml.etree.ElementTree import Element, SubElement, tostring

TIMEOUT = 2

_LOGGER = logging.getLogger(__name__)

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
KEY_PICTURE_IN_PICTURE = "Key.Pip"
KEY_SCREENSHOT = "Key.Screenshot"
KEY_APP_SWITCH = "Key.APP.Switch"

CONF_PORT = 9529


class ZidooRC(object):
    def __init__(self, host, psk=None, mac=None):
        """Initialize the Zidoo RC class.
        MAC address is optional but necessary if we want to turn on the TV.
        If PSK is not passed then standard basic auth is used.
        """

        self._host = "{}:{}".format(host, CONF_PORT)
        self._mac = mac
        self._psk = psk
        self._cookies = None
        self._commands = []
        self._content_mapping = []
        self._current_source = None
        self._app_list = {}

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

    def connect(self, clientid, nickname):
        """Connect to TV and get authentication cookie.
        Parameters
        ---------
        clientid: str
            Client ID.
        nickname: str
            Client human friendly name.
        Returns
        -------
        bool
            True if connected.
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

        url = "http://%s/ZidooControlCenter/getModel" % self._host
        try:
            response = requests.post(
                url, data=authorization, headers=headers, timeout=TIMEOUT, auth=auth
            )
            response.raise_for_status()

        except requests.exceptions.HTTPError as exception_instance:
            _LOGGER.error("[W] HTTPError: " + str(exception_instance))
            return False

        except requests.exceptions.Timeout as exception_instance:
            _LOGGER.error("[W] Timeout occurred: " + str(exception_instance))
            return False

        except Exception as exception_instance:  # pylint: disable=broad-except
            _LOGGER.error("[W] Exception: " + str(exception_instance))
            return False

        else:
            resp = response.json()
            # _LOGGER.debug(json.dumps(resp, indent=4))
            if resp is not None or resp.get("status") == 200:
                self._cookies = response.cookies
                # _LOGGER.debug("cookie: " + str(response.cookies))
                if self._mac is None:
                    self._mac = resp.get("net_mac")
                return True

        return False

    def is_connected(self):
        if self._cookies is None:
            return False
        else:
            return True

    def update(self):

        resp = get_play_status()
        _LOGGER.info("[W] Update: " + str(resp))

    def _wakeonlan(self):
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

    def zidoo_send_key(self, key, log_error=True):
        url = "ZidooControlCenter/RemoteControl/sendkey"
        params = {"key": key}

        return self.zidoo_req_json(url, params)

    def zidoo_req_json(self, url, params={}, log_errors=True):
        """ Send request command via HTTP json to Zidoo Device."""

        headers = {}
        if self._psk is not None:
            headers["X-Auth-PSK"] = self._psk

        url = "http://{}/{}".format(self._host, url)

        try:
            response = requests.get(
                url, params, cookies=self._cookies, timeout=TIMEOUT, headers=headers
            )

        except requests.exceptions.HTTPError as exception_instance:
            if log_errors:
                _LOGGER.error("HTTPError: " + str(exception_instance))

        except Exception as exception_instance:  # pylint: disable=broad-except
            if log_errors:
                _LOGGER.error("Exception: " + str(exception_instance))

        else:
            html = json.loads(response.content.decode("utf-8"))
            return html

    def play_content(self, uri):
        """Play content by URI."""
        url = "ZidooFileControl/openFile?path={}&videoplaymode={}".format(uri, 0)

        response = self.zidoo_req_json(url)

        if response and response.get("status") == 200:
            return response

    """
    Play Movie
    /ZidooPoster/PlayVideo?id=' + id + '&type=' + type
    """

    """
    Get Poster
    GET/ZidooPoster/getFile/getPoster?id=id&w=width&hheight
    """

    """
    Search for Movie using name or person
    GET/ZidooPoster/search?q=x&type=0&page=page&pagesize=size
    ZidooPoster/search/person?name=' + keywords
    """

    def get_source(self, source):
        """Returns list of Sources"""
        return self._current_source

    def load_source_list(self):
        """ Load App list from Zidoo device."""
        return self.get_app_list()

    def get_playing_info(self):
        return_value = {}

        response = self._get_video_playing_info()
        if response is not None:
            return_value = response
            return_value["source"] = "video"
            return return_value

        response = self._get_music_playing_info()
        if response is not None:
            return_value = response
            return_value["source"] = "music"
            return return_value

        return None

    def _get_video_playing_info(self):
        """Get information on program that is shown on TV."""
        return_value = {}
        response = self.zidoo_req_json("ZidooVideoPlay/getPlayStatus")

        # _LOGGER.debug(json.dumps(response, indent=4))
        if response is not None and response.get("status") == 200:
            if response.get("video"):
                result = response.get("video")
                return_value["status"] = result.get("status")
                return_value["title"] = result.get("title")
                return_value["uri"] = result.get("path")
                return_value["duration"] = result.get("duration")
                return_value["position"] = result.get("currentPosition")
                return return_value
        return None

    def _get_music_playing_info(self):
        return_value = {}
        response = self.zidoo_req_json("ZidooMusicControl/getPlayStatus")

        # _LOGGER.debug(json.dumps(response, indent=4))
        if response is not None and response.get("status") == 200:
            return_value["status"] = response.get("isPlay")
            if response.get("music"):
                result = response.get("music")
                return_value["title"] = result.get("title")
                return_value["artist"] = result.get("artist")
                return_value["uri"] = result.get("uri")

                result = response.get("state")
                return_value["duration"] = result.get("duration")
                return_value["position"] = result.get("position")
                return return_value
        return None

    def _get_movie_playing_info(self):
        return_value = {}

        response = self.zidoo_req_json("ZidooControlCenter/getPlayStatus")

        if response is not None and response.get("status") == 200:
            if response.get("file"):
                result = response.get("file")
                return_value["status"] = result.get("status")
                return_value["title"] = result.get("title")
                return_value["uri"] = result.get("path")
                return_value["duration"] = result.get("duration")
                return_value["position"] = result.get("currentPosition")
                return return_value
        return None

    def get_play_modes(self):
        """Get info on TV."""
        return_value = {}
        response = self.zidoo_req_json("ZidooVideoPlay/getPlayModeList")

        if response is not None and response.get("status") == 200:
            result = response  # .get('result')[0]
            return_value["name"] = result.get("model")
            return_value["model"] = result.get("model")
            return_value["language"] = result.get("language")
        return return_value

    def get_play_status(self):
        """Get info on TV."""
        return_value = {}
        response = self.zidoo_req_json("ZidooVideoPlay/getPlayStatus")

        if response is not None and response.get("status") == 200:
            result = response  # .get('result')[0]
            return_value["name"] = result.get("model")
            return_value["model"] = result.get("model")
            return_value["language"] = result.get("language")
        return return_value

    def get_system_info(self):
        """Get info on TV."""
        return_value = {}
        response = self.zidoo_req_json("ZidooControlCenter/getModel")

        if response is not None and response.get("status") == 200:
            result = response  # .get('result')[0]
            return_value["name"] = result.get("model")
            return_value["model"] = result.get("model")
            return_value["language"] = result.get("language")
            return return_value

    def get_power_status(self):
        """Get power status: off, active, standby.
        By default the TV is turned off."""
        return_value = "off"

        try:
            response = self.zidoo_req_json("ZidooControlCenter/getModel")

            if response is not None:
                return_value = "on"
        except:  # pylint: disable=broad-except
            pass
        return return_value

    def get_volume_info(self):
        """Get volume info.
        ? Not currently supported."""
        return None

    def set_volume_level(self, volume):
        """Set volume level.
        ? Not currently supported."""
        # api_volume = str(int(round(volume * 100)))

    def _recreate_auth_cookie(self):
        """
        The default cookie is for URL/sony.
        For some commands we need it for the root path
        """
        cookies = requests.cookies.RequestsCookieJar()
        cookies.set("auth", self._cookies.get("auth"))
        return cookies

    def get_app_list(self, log_errors=True):
        """Get the list of installed apps"""
        return_values = {}

        response = self.zidoo_req_json("ZidooControlCenter/Apps/getApps")

        if response is not None and response.get("status") == 200:
            for result in response["apps"]:
                if result.get("isCanOpen"):
                    name = result.get("label")
                    id = result.get("packageName")
                    return_values[name] = id

        return return_values

    def start_app(self, app_name, log_errors=True):
        """Start an app by name """
        if len(self._app_list) == 0:
            self._app_list = self.get_app_list(log_errors)
        if app_name in self._app_list:
            return self._start_app(self._app_list[app_name], log_errors=log_errors)

    def _start_app(self, app_id, log_errors=True):
        """Start an app by id"""
        headers = {}

        if self._psk is not None:
            headers["X-Auth-PSK"] = self._psk

        url = "http://{}/ZidooControlCenter/Apps/openApp?packageName={}".format(
            self._host, app_id
        )

        try:
            # printf(url)
            cookies = self._recreate_auth_cookie()
            response = requests.post(
                url, cookies=cookies, timeout=TIMEOUT, headers=headers
            )
        except requests.exceptions.HTTPError as exception_instance:
            if log_errors:
                _LOGGER.error("HTTPError: " + str(exception_instance))

        except Exception as exception_instance:  # pylint: disable=broad-except
            if log_errors:
                _LOGGER.error("Exception: " + str(exception_instance))
        else:
            content = response.content
            return content

    def select_source(self, source):
        """Set the input source."""
        if len(self._content_mapping) == 0:
            self._content_mapping = self.load_source_list()
        if source in self._content_mapping:
            uri = self._content_mapping[source]
            self.play_content(uri)

    def turn_on(self):
        """Turn the media player on."""
        self._wakeonlan()
        # Try using the power on command incase the WOL doesn't work
        if self.get_power_status() != "active":
            self.zidoo_send_key(ZKEY_POWER_ON)

    def turn_off(self):
        """Turn off media player."""
        self.zidoo_send_key(ZKEY_POWER_STANDBY)

    def volume_up(self):
        """Volume up the media player."""
        self.zidoo_send_key(ZKEY_VOLUME_UP)

    def volume_down(self):
        """Volume down media player."""
        self.zidoo_send_key(ZKEY_VOLUME_DOWN)

    def mute_volume(self):
        """Send mute command."""
        self.zidoo_send_key(ZKEY_MUTE)

    def media_play(self):
        """Send play command."""
        # self.zidoo_send_key(ZKEY_OK)
        self.zidoo_send_key(ZKEY_MEDIA_PLAY)

    def media_pause(self):
        """Send media pause command to media player."""
        self.zidoo_send_key(ZKEY_MEDIA_PAUSE)

    def media_stop(self):
        """Send media pause command to media player."""
        self.zidoo_send_key(ZKEY_MEDIA_STOP)

    def media_next_track(self):
        """Send next track command."""
        self.zidoo_send_key(ZKEY_MEDIA_NEXT)

    def media_previous_track(self):
        """Send the previous track command."""
        self.zidoo_send_key(ZKEY_MEDIA_PREVIOUS)

    def calc_time(self, *times):
        """Calculate the sum of times, value is returned in HH:MM."""
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
        """Give starttime, endtime and percentage played.
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
