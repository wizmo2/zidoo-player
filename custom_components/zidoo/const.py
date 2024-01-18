"""Constants for Zidoo component."""
import logging
from .zidooaio import (
    ZTYPE_VIDEO,
    ZTYPE_MOVIE,
    ZTYPE_TV_SHOW,
    ZTYPE_TV_SEASON,
    ZTYPE_TV_EPISODE,
    ZTYPE_COLLECTION,
    ZTYPE_OTHER,
)
from homeassistant.components.media_player import MediaClass, MediaType

_LOGGER = logging.getLogger(__package__)

DOMAIN = "zidoo"
DATA_ZIDOO_CONFIG = "zidoo_config"
VERSION = "1.1.1"
DATA = "data"
UPDATE_TRACK = "update_track"
UPDATE_LISTENER = "update_listener"

MANUFACTURER = "Zidoo"

CLIENTID_PREFIX = "home-assistant"
CLIENTID_NICKNAME = "Home Assistant"

CONF_SHORTCUT = "shortcut_json"
CONF_POWERMODE = "powermode"

SUBTITLE_SERVICE = "set_subtitle"
AUDIO_SERVICE = "set_audio"
BUTTON_SERVICE = "send_key"

# Triggers
EVENT_TURN_ON = "zidoo.turn_on"
EVENT_TURN_OFF = "zidoo.turn_off"

MEDIA_TYPE_FILE = "file"

ZSHORTCUTS = [
    {"name": "FAVORITES", "path": "favorite", "type": MediaType.VIDEO},
    {"name": "LATEST", "path": "recent", "type": MediaType.VIDEO, "default": True},
    {"name": "WATCHING", "path": "watching", "type": MediaType.VIDEO},
    {"name": "SD", "path": "sd", "type": MediaType.VIDEO},
    {"name": "DISC", "path": "bluray", "type": MediaType.VIDEO},
    {"name": "UHD", "path": "4k", "type": MediaType.VIDEO},
    {"name": "3D", "path": "3d", "type": MediaType.VIDEO},
    {"name": "KIDS", "path": "children", "type": MediaType.GENRE},
    {"name": "UNWATCHED", "path": "unwatched", "type": MediaType.VIDEO},
    {"name": "OTHER", "path": "other", "type": MediaType.VIDEO},
    {"name": "ALL", "path": "all", "type": MediaType.VIDEO},
    {"name": "MOVIES", "path": "movie", "type": MediaType.MOVIE, "default": True},
    {"name": "TV SHOWS", "path": "tvshow", "type": MediaType.TVSHOW, "default": True},
    {"name": "MUSIC", "path": "music", "type": MediaType.MUSIC, "default": True},
    {"name": "ALBUMS", "path": "album", "type": MediaType.ALBUM},
    {"name": "ARTISTS", "path": "artist", "type": MediaType.ARTIST},
    {"name": "PLAYLISTS", "path": "playlist", "type": MediaType.PLAYLIST},
]
ZDEFAULT_SHORTCUTS = ["recent", "movie", "tvshow"]

ITEM_TYPE_MEDIA_CLASS = {
    MediaType.MUSIC: MediaClass.PLAYLIST,  # MediaClass.MUSIC,
    MediaType.ALBUM: MediaClass.ALBUM,
    MediaType.ARTIST: MediaClass.ARTIST,
    MediaType.GENRE: MediaClass.GENRE,
    MediaType.EPISODE: MediaClass.EPISODE,
    MediaType.MOVIE: MediaClass.MOVIE,
    MediaType.PLAYLIST: MediaClass.PLAYLIST,
    MediaType.SEASON: MediaClass.SEASON,
    MediaType.TVSHOW: MediaClass.TV_SHOW,
    MediaType.TRACK: MediaClass.TRACK,
    MediaType.VIDEO: MediaClass.VIDEO,
    MEDIA_TYPE_FILE: MediaClass.DIRECTORY,
    MediaType.CHANNEL: MediaClass.CHANNEL,
    MediaType.IMAGE: MediaClass.IMAGE,
    MediaType.APP: MediaClass.APP,
    MediaType.PODCAST: MediaClass.PODCAST,
    MediaType.URL: MediaClass.URL,
}

ZCONTENT_ITEM_TYPE = {
    0: MEDIA_TYPE_FILE,  # folder
    1: MediaType.TRACK,  # music
    2: MediaType.VIDEO,  # video
    3: MediaType.IMAGE,  # image
    # 4: 'text', # 5: 'apk', # 6: 'pdf', # 7: 'document', # 8: 'spreadsheet', # 9: 'presentation', # 10: 'web', # 11: 'archive' ,  # 12: 'other'
    1000: MEDIA_TYPE_FILE,  # hhd
    1001: MEDIA_TYPE_FILE,  # usb
    1002: MEDIA_TYPE_FILE,  # usb
    1003: MEDIA_TYPE_FILE,  # tf
    1004: MediaType.URL,  # nfs
    1005: MediaType.URL,  # smb
    1006: MEDIA_TYPE_FILE,
    1007: MEDIA_TYPE_FILE,
    1008: MEDIA_TYPE_FILE,
}

ZTYPE_MEDIA_CLASS = {
    ZTYPE_VIDEO: MediaClass.VIDEO,
    ZTYPE_MOVIE: MediaClass.MOVIE,
    ZTYPE_COLLECTION: MediaClass.MOVIE,
    ZTYPE_TV_SHOW: MediaClass.TV_SHOW,
    ZTYPE_TV_SEASON: MediaClass.SEASON,
    ZTYPE_TV_EPISODE: MediaClass.TRACK,  # MediaClass.EPISODE, # no episode images with zidoo
    6: MediaClass.TRACK,  # Other
    7: MediaClass.TRACK,  # Dummy for +1
}

ZTYPE_MEDIA_TYPE = {
    ZTYPE_VIDEO: MediaType.VIDEO,
    ZTYPE_MOVIE: MediaType.MOVIE,
    ZTYPE_COLLECTION: MediaType.MOVIE,
    ZTYPE_TV_SHOW: MediaType.TVSHOW,
    ZTYPE_TV_SEASON: MediaType.SEASON,
    ZTYPE_TV_EPISODE: MediaType.EPISODE,  # no episode images with zidoo
    ZTYPE_OTHER: MediaType.TRACK,
    7: MediaType.TRACK,  # Dummy for +1
}
