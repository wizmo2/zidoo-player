"""Constants for Zidoo component."""
import logging
from .zidoorc import (
    ZTYPE_VIDEO,
    ZTYPE_MOVIE,
    ZTYPE_TV_SHOW,
    ZTYPE_TV_SEASON,
    ZTYPE_TV_EPISODE,
    ZTYPE_COLLECTION,
    ZTYPE_OTHER,
)
from homeassistant.components.media_player.const import (
    MEDIA_CLASS_ALBUM,
    MEDIA_CLASS_ARTIST,
    MEDIA_CLASS_CHANNEL,
    MEDIA_CLASS_GENRE,
    MEDIA_CLASS_DIRECTORY,
    MEDIA_CLASS_EPISODE,
    MEDIA_CLASS_MOVIE,
    MEDIA_CLASS_PLAYLIST,
    MEDIA_CLASS_TRACK,
    MEDIA_CLASS_SEASON,
    MEDIA_CLASS_TV_SHOW,
    MEDIA_CLASS_VIDEO,
    MEDIA_CLASS_APP,
    MEDIA_CLASS_IMAGE,
    MEDIA_CLASS_URL,
    MEDIA_CLASS_MUSIC,
    MEDIA_CLASS_PODCAST,
    MEDIA_TYPE_CHANNEL,
    MEDIA_TYPE_MUSIC,
    MEDIA_TYPE_ALBUM,
    MEDIA_TYPE_ARTIST,
    MEDIA_TYPE_GENRE,
    MEDIA_TYPE_PLAYLIST,
    MEDIA_TYPE_TRACK,
    MEDIA_TYPE_SEASON,
    MEDIA_TYPE_MOVIE,
    MEDIA_TYPE_TVSHOW,
    MEDIA_TYPE_EPISODE,
    MEDIA_TYPE_VIDEO,
    MEDIA_TYPE_URL,
    MEDIA_TYPE_APP,
    MEDIA_TYPE_IMAGE,
    MEDIA_TYPE_PODCAST,
)

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
    # {"name": "DOWNLOADS", "path": "/tmp/ramfs/mnt/192.168.1.1%23SHARED/DOWNLOAD", "type": MEDIA_TYPE_FILE},
    {"name": "FAVORITES", "path": "favorite", "type": MEDIA_TYPE_VIDEO},
    {"name": "LATEST", "path": "recent", "type": MEDIA_TYPE_VIDEO, "default": True},
    {"name": "WATCHING", "path": "watching", "type": MEDIA_TYPE_VIDEO},
    {"name": "SD", "path": "sd", "type": MEDIA_TYPE_VIDEO},
    {"name": "DISC", "path": "bluray", "type": MEDIA_TYPE_VIDEO},
    {"name": "UHD", "path": "4k", "type": MEDIA_TYPE_VIDEO},
    {"name": "3D", "path": "3d", "type": MEDIA_TYPE_VIDEO},
    {"name": "KIDS", "path": "children", "type": MEDIA_TYPE_GENRE},
    {"name": "UNWATCHED", "path": "unwatched", "type": MEDIA_TYPE_VIDEO},
    {"name": "OTHER", "path": "other", "type": MEDIA_TYPE_VIDEO},
    {"name": "ALL", "path": "all", "type": MEDIA_TYPE_VIDEO},
    {"name": "MOVIES", "path": "movie", "type": MEDIA_TYPE_MOVIE, "default": True},
    {"name": "TV SHOWS", "path": "tvshow", "type": MEDIA_TYPE_TVSHOW, "default": True},
]
ZDEFAULT_SHORTCUTS = ["recent", "movie", "tvshow"]

ITEM_TYPE_MEDIA_CLASS = {
    MEDIA_TYPE_MUSIC: MEDIA_CLASS_MUSIC,
    MEDIA_TYPE_ALBUM: MEDIA_CLASS_ALBUM,
    MEDIA_TYPE_ARTIST: MEDIA_CLASS_ARTIST,
    MEDIA_TYPE_GENRE: MEDIA_CLASS_GENRE,
    MEDIA_TYPE_EPISODE: MEDIA_CLASS_EPISODE,
    MEDIA_TYPE_MOVIE: MEDIA_CLASS_MOVIE,
    MEDIA_TYPE_PLAYLIST: MEDIA_CLASS_PLAYLIST,
    MEDIA_TYPE_SEASON: MEDIA_CLASS_SEASON,
    MEDIA_TYPE_TVSHOW: MEDIA_CLASS_TV_SHOW,
    MEDIA_TYPE_TRACK: MEDIA_CLASS_TRACK,
    MEDIA_TYPE_VIDEO: MEDIA_CLASS_VIDEO,
    MEDIA_TYPE_FILE: MEDIA_CLASS_DIRECTORY,
    MEDIA_TYPE_CHANNEL: MEDIA_CLASS_CHANNEL,
    MEDIA_TYPE_IMAGE: MEDIA_CLASS_IMAGE,
    MEDIA_TYPE_APP: MEDIA_CLASS_APP,
    MEDIA_TYPE_PODCAST: MEDIA_CLASS_PODCAST,
    MEDIA_TYPE_URL: MEDIA_CLASS_URL,
}

ZCONTENT_ITEM_TYPE = {
    0: MEDIA_TYPE_FILE,  # folder
    1: MEDIA_TYPE_TRACK,  # music
    2: MEDIA_TYPE_VIDEO,  # video
    3: MEDIA_TYPE_IMAGE,  # image
    # 4: 'text', # 5: 'apk', # 6: 'pdf', # 7: 'document', # 8: 'spreadsheet', # 9: 'presentation', # 10: 'web', # 11: 'archive' ,  # 12: 'other'
    1000: MEDIA_TYPE_FILE,  # hhd
    1001: MEDIA_TYPE_FILE,  # usb
    1002: MEDIA_TYPE_FILE,  # usb
    1003: MEDIA_TYPE_FILE,  # tf
    1004: MEDIA_TYPE_URL,  # nfs
    1005: MEDIA_TYPE_URL,  # smb
    1006: MEDIA_TYPE_FILE,
    1007: MEDIA_TYPE_FILE,
    1008: MEDIA_TYPE_FILE,
}

ZTYPE_MEDIA_CLASS = {
    ZTYPE_VIDEO: MEDIA_CLASS_VIDEO,
    ZTYPE_MOVIE: MEDIA_CLASS_MOVIE,
    ZTYPE_COLLECTION: MEDIA_CLASS_MOVIE,
    ZTYPE_TV_SHOW: MEDIA_CLASS_TV_SHOW,
    ZTYPE_TV_SEASON: MEDIA_CLASS_SEASON,
    ZTYPE_TV_EPISODE: MEDIA_CLASS_TRACK,  # MEDIA_CLASS_EPISODE, # no episode images with zidoo
    6: MEDIA_CLASS_TRACK,  # Other
    7: MEDIA_CLASS_TRACK,  # Dummy for +1
}

ZTYPE_MEDIA_TYPE = {
    ZTYPE_VIDEO: MEDIA_TYPE_VIDEO,
    ZTYPE_MOVIE: MEDIA_TYPE_MOVIE,
    ZTYPE_COLLECTION: MEDIA_TYPE_MOVIE,
    ZTYPE_TV_SHOW: MEDIA_TYPE_TVSHOW,
    ZTYPE_TV_SEASON: MEDIA_TYPE_SEASON,
    ZTYPE_TV_EPISODE: MEDIA_TYPE_EPISODE,  # no episode images with zidoo
    ZTYPE_OTHER: MEDIA_TYPE_TRACK,
    7: MEDIA_CLASS_TRACK,  # Dummy for +1
}
