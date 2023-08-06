# API Commands

"""
Zidoo Remote Control API
By Wizmo
References
    oem v1: https://www.zidoo.tv/Support/developer/
    oem v2: http://apidoc.zidoo.tv/s/98365225
"""

ZCMD_GETMODEL = "ZidooControlCenter/getModel"
ZCMD_SENDKEY = "ZidooControlCenter/RemoteControl/sendkey"
ZCMD_VIDEOSTATUS = "ZidooVideoPlay/" + ZCMD_STATUS
ZCMD_MUSICSTATUS = "ZidooMusicControl/" + ZCMD_STATUS
ZCMD_FILELOOKUP = "ZidooPoster/v2/getAggregationOfFile?path={}"
ZCMD_PLAYMODES = "ZidooVideoPlay/getPlayModeList"
ZCMD_SUBTITLELIST =  "ZidooVideoPlay/getSubtitleList"
ZCMD_AUDIOLIST = "ZidooVideoPlay/getAudioList"

            "ZidooVideoPlay/setAudio?index={}".format(index), log_errors=False
        response = self._req_json("ZidooControlCenter/getModel")
            "ZidooControlCenter/Apps/getApps", log_errors=log_errors
            "ZidooControlCenter/Apps/openApp?packageName={}".format(app_id)
        response = self._req_json("ZidooFileControl/getDevices")
        # v2 http://{{host}}/Poster/v2/getAggregations?type=0&start=0&count=40
            "ZidooPoster/getVideoList?page=1&pagesize={}&type={}".format(
                max_count, filter_type
            )
        response = self._req_json("ZidooPoster/getCollection?id={}".format(movie_id))
        # v1 response = self._req_json("ZidooPoster/getDetail?id={}".format(movie_id))
        response = self._req_json("Poster/v2/getDetail?id={}".format(movie_id))

            "MusicControl/v2/getSingleMusics?start=0&count={}".format(max_count)
                "MusicControl/v2/getAlbumMusics?id={}&start=0&count={}".format(
                    album_id, max_count
                )
            )
                "MusicControl/v2/getAlbums?start=0&count={}".format(max_count)
                "MusicControl/v2/getArtistMusics?id={}&start=0&count={}".format(
                    artist_id, max_count
                )
            )
            response = self._req_json(
                "MusicControl/v2/getArtists?start=0&count={}".format(max_count)
            )
            return response

                    "MusicControl/v2/getPlayQueue?start=0&count={}".format(max_count)
                )
            else:
                response = self._req_json(
                    "MusicControl/v2/getSongListMusics?id={}&start=0&count={}".format(
                        playlist_id, max_count
                    )
                )
            response = self._req_json(
                # "MusicControl/v2/getSongList?start=0&count={}".format(max_count)
                "MusicControl/v2/getSongLists"
            )
        # v1 "ZidooPoster/search?q={}&type={}&page=1&pagesize={}".format(query, filter_type, max_count)
        response = self._req_json(
            "Poster/v2/searchAggregation?q={}&type={}&start=0&count={}".format(
                query, search_type, max_count
            )
        )
        response = self._req_json(
            "MusicControl/v2/searchMusic?key={}&start=0&count={}".format(
                query, max_count
            )
        )
        response = self._req_json(
            "MusicControl/v2/searchAlbum?key={}&start=0&count={}".format(
                query, max_count
            ),
            timeout=10,
        )

        response = self._req_json(
            "MusicControl/v2/searchArtist?key={}&start=0&count={}".format(
                query, max_count
            )
        )

        if response is not None:  # and response.get("status") == 200:
            return response

    def play_file(self, uri):
        """Play content by URI.
        Parameters
            uri: str
                path of file to play.
        Returns
            True if sucessful
        """
        url = "ZidooFileControl/openFile?path={}&videoplaymode={}".format(uri, 0) # has issues with parsing for local files

        response = self._req_json(url)

        if response and response.get("status") == 200:
            return True
        return False

    def play_stream(self, uri, media_type):
        """Play url by type
        Uses undocumented v2 upnp FileOpen calls using 'res' and 'type'
            res: str = quoted url
            type : int = app launch
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
        Parmeters:
            uri: str
                uri link to stream
            media_type: int
                See ZTYPE_MIMETYPE
        Returns
            True if sucessful
        """
        # the res uri needs to be double quoted to protect keys etc.
        # use safe='' in quote to force "/" quoting
        uri = urllib.parse.quote(uri, safe="")

        upnp = "upnp://{}/{}?type={}&res={}".format(
            ZUPNP_SERVERNAME, VERSION, media_type, uri
        )
        url = "ZidooFileControl/v2/openFile?url={}".format(
            urllib.parse.quote(upnp, safe="")
        )
        _LOGGER.debug("Stream command %s", str(url))

        response = self._req_json(url)

        if response and response.get("code") == 0:
            return True
        return False

    def play_movie(self, movie_id, video_type=-1):
        """Play video content by Movie id.
        Parameters
            movie_id
                database id
        Returns
            True if sucessfuL
        """
        # uses the agreggateid to find the first video to play
        if video_type != 0:
            movie_id = self._collection_video_id(movie_id)
        # print("Video id : {}".format(video_id))

        # v2 http://{}/VideoPlay/playVideo?index=0
        response = self._req_json(
            "ZidooPoster/PlayVideo?id={}&type={}".format(movie_id, video_type)
        )

        if response and response.get("status") == 200:
            return True
        return False

    def play_music(self, media_id, media_type="music", music_id=None):
        """Play video content by id.
        Parameters
            media_id
                database id for media type (or ids for music type)
            media_type
                see ZMUSIC_SEARCH_TYPE
            music_id
                database id for track to play (use None or -1 for first)
        Returns
            True if sucessfuL
        """
        if media_type in ZMUSIC_PLAYLISTTYPE:
            response = self._req_json(
                "MusicControl/v2/playMusic?type={}&id={}&musicId={}&music_type=0&trackIndex=1&sort=0".format(
                    ZMUSIC_PLAYLISTTYPE[media_type], media_id, music_id
                )
            )
        else:  # music
            response = self._req_json(
                "MusicControl/v2/playMusics?ids={}&musicId={}&trackIndex=-1".format(
                    media_id, music_id
                )
            )

        if response and response.get("status") == 200:
            return True
        return False

    def get_video_playlist(self):
        """get the current video playlist
        Returns
            json if successful
                'status': 200
                'size': count
                'playList' : array
                    'title': video name (file name)
                    'index': int
        """
        response = self._req_json("VideoPlay/getPlaylist")

        if response and response.get("status") == 200:
            return response

    def get_music_playlist(self, max_count=DEFAULT_COUNT):
        """Gets the current music player playlist
        Parameters
            max_count: int
                list size limit
        Returns
            raw api response if sucessful
        """
        response = self._req_json(
            "MusicControl/v2/getPlayQueue?start=0&count={}".format(max_count)
        )

        if response is not None and response.get("status") == 200:
            return response

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
                    'isBDMV': True if ?high definition
                    'isBluray': True if blue ray resolution
                    'length': length in ms
                    'modifyDate': linux date code
        """
        response = self._req_json(
            "ZidooFileControl/getFileList?path={}&type={}".format(uri, file_type)
        )

        if response is not None and response.get("status") == 200:
            return response

    def get_host_list(self, uri, host_type=1005):
        """get host list of saved network shares
        Returns
            json if sucessful
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
        response = self._req_json(
            "ZidooFileControl/getHost?path={}&type={}".format(uri, host_type)
        )
        _LOGGER.debug("zidoo host list: %s", str(response))

        return_value = {}
        share_list = []
        if response is not None and response.get("status") == 200:
            return_value["status"] = 200
            hosts = response["hosts"]
            for item in hosts:
                response = self.get_file_list(item.get("ip"), item.get("type"))
                hostname = item.get("name").split("/")[-1]
                if response is not None and response.get("status") == 200:
                    for share in response["filelist"]:
                        share["name"] = hostname + "/" + share.get("name")
                        share_list.append(share)
        return_value["filelist"] = share_list
        return return_value

    def generate_image_url(self, media_id, media_type, width=400, height=None):
        """Get link to thumbnail"""
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

    def _generate_movie_image_url(self, movie_id, width=400, height=600):
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
        # http://{}/Poster/v2/getPoster?id=66&w=60&h=30
        url = "http://{}/ZidooPoster/getFile/getPoster?id={}&w={}&h={}".format(
            self._host, movie_id, width, height
        )

        return url

    def _generate_music_image_url(self, music_id, music_type=0, width=200, height=200):
        """Get link to thumbnail
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
        url = "http://{}/ZidooMusicControl/v2/getImage?id={}&music_type={}&type={}&target={}".format(
            self._host,
            music_id,
            ZMUSIC_IMAGETYPE[music_type],
            music_type,
            ZMUSIC_IMAGETARGET[music_type],
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
            url = "http://{}/ZidooMusicControl/v2/getImage?id={}&music_type={}&type=4&target=16".format(
                self._host, self._music_id, self._music_type
            )

        # _LOGGER.debug("zidoo getting current image: url-{}".format(url))
        return url

    def turn_on(self):
        """Turn the media player on."""
        # Try using the power on command incase the WOL doesn't work
        self._send_key(ZKEY_POWER_ON, False)
        self._wakeonlan()

    def turn_off(self, standby=False):
        """Turn off media player."""
        key = ZKEY_POWER_OFF
        if standby:
            key = ZKEY_POWER_STANDBY
        self._send_key(key)

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
        if self._current_source == ZCONTENT_NONE and self._last_video_path:
            self.play_file(self._last_video_path)
        elif (self._current_source == ZCONTENT_MUSIC):
            self._req_json("MusicControl/v2/playOrPause")
        else:
            self._send_key(ZKEY_MEDIA_PLAY)

    def media_pause(self):
        """Send media pause command to media player."""
        if (self._current_source == ZCONTENT_MUSIC):
            self._req_json("MusicControl/v2/playOrPause")
        else:
            self._send_key(ZKEY_MEDIA_PAUSE)

    def media_stop(self):
        """Send media pause command to media player."""
        self._send_key(ZKEY_MEDIA_STOP)

    def media_next_track(self):
        """Send next track command."""
        if (self._current_source == ZCONTENT_MUSIC):
            self._req_json("MusicControl/v2/playNext")
        else:
            self._send_key(ZKEY_MEDIA_NEXT)

    def media_previous_track(self):
        """Send the previous track command."""
        if (self._current_source == ZCONTENT_MUSIC):
            self._req_json("MusicControl/v2/playLast")
        else:
            self._send_key(ZKEY_MEDIA_PREVIOUS)

    def set_media_position(self, position, durationsec=1):
        """Set the current playing position.
        Parameters
            position
                position in ms
        Return
            True if sucessful
        """
        if self._current_source == ZCONTENT_VIDEO:
            response = self._set_movie_position(position)
        elif self._current_source == ZCONTENT_MUSIC:
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
