"""Support for media browsing."""
from homeassistant.components.media_player import BrowseError, BrowseMedia
from homeassistant.components.media_player.const import (
    MEDIA_CLASS_ALBUM,
    MEDIA_CLASS_ARTIST,
    MEDIA_CLASS_GENRE,
    MEDIA_CLASS_DIRECTORY,
    MEDIA_CLASS_EPISODE,
    MEDIA_CLASS_MOVIE,
    MEDIA_CLASS_PLAYLIST,
    MEDIA_CLASS_TRACK,
    MEDIA_CLASS_SEASON,
    MEDIA_CLASS_TV_SHOW,
    MEDIA_CLASS_VIDEO,
    MEDIA_TYPE_ALBUM,
    MEDIA_TYPE_ARTIST,
    MEDIA_TYPE_GENRE,
    MEDIA_TYPE_PLAYLIST,
    MEDIA_TYPE_TRACK,
    MEDIA_TYPE_MOVIE,
    MEDIA_TYPE_TVSHOW,
    MEDIA_TYPE_URL,
)

BROWSE_LIMIT = 1000

ITEM_TYPE_MEDIA_CLASS = {
    "album": MEDIA_CLASS_ALBUM,
    "artist": MEDIA_CLASS_ARTIST,
    "episode": MEDIA_CLASS_EPISODE,
    "movie": MEDIA_CLASS_MOVIE,
    "playlist": MEDIA_CLASS_PLAYLIST,
    "season": MEDIA_CLASS_SEASON,
    "tvshow": MEDIA_CLASS_TV_SHOW,
    "track": MEDIA_CLASS_TRACK,
    "video": MEDIA_CLASS_VIDEO,
    "file": MEDIA_CLASS_DIRECTORY,
}

MOVIE_TYPE_MEDIA_CLASS = {
    0: MEDIA_CLASS_VIDEO,
    1: MEDIA_CLASS_MOVIE,
    2: MEDIA_CLASS_TRACK,
    3: MEDIA_CLASS_TV_SHOW,
    4: MEDIA_CLASS_SEASON,
    5: MEDIA_CLASS_TRACK,  # MEDIA_CLASS_EPISODE, # no episode images with zidoo
    6: MEDIA_CLASS_TRACK,
    7: MEDIA_CLASS_TRACK,
}

CONTENT_ITEM_TYPE = {
    0: "file",
    1: "track",
    2: "video",
    # 3: 'image', # 4: 'text', # 5: 'apk', # 6: 'pdf', # 7: 'document', # 8: 'spreadsheet', # 9: 'presentation', # 10: 'web', # 11: 'archive' ,  # 12: 'other'
    1000: "file",  # hhd
    1001: "file",  # usb
    1002: "file",  # usb
    1003: "file",  # tf
    1004: "file",  # nfs
    1005: "file",  # smb
    1006: "file",
    1007: "file",
    1008: "file",
}

FAVORITES = [
#    {"name": "DOWNLOADS", "path": "/tmp/ramfs/mnt/192.168.1.1%23SHARED/DOWNLOAD"},
#    {"name": "AUDIO", "path": "/tmp/ramfs/mnt/192.168.1.1%23SHARED/AUDIO"},
]


def browse_media(  # noqa: C901
    entity, is_internal, media_content_type=None, media_content_id=None
):
    """Implement the websocket media browsing helper."""

    def build_item_response(player, payload):
        """Create response payload for search described by payload."""

        search_id = payload["search_id"]
        search_type = payload["search_type"]

        media_class = ITEM_TYPE_MEDIA_CLASS[search_type]
        child_media_class = MEDIA_CLASS_DIRECTORY
        children = None
        title = "Zidoo Media"

        if media_class == MEDIA_CLASS_DIRECTORY:
            result = player.get_file_list(search_id)

            if result is not None and result.get("filelist"):

                children = []
                for item in result["filelist"]:
                    content_type = item["type"]
                    item_type = None
                    if content_type is not None and content_type in CONTENT_ITEM_TYPE:
                        item_type = CONTENT_ITEM_TYPE[content_type]
                    if item_type is not None:
                        child_media_class = ITEM_TYPE_MEDIA_CLASS[item_type]
                        item_thumbnail = None

                        children.append(
                            BrowseMedia(
                                title=item["name"],
                                media_class=child_media_class,
                                media_content_id=item["path"],
                                media_content_type=item_type,
                                can_play=True,
                                can_expand=child_media_class == MEDIA_CLASS_DIRECTORY,
                                thumbnail=item_thumbnail,
                            )
                        )

        if media_class == MEDIA_CLASS_MOVIE or media_class == MEDIA_CLASS_TV_SHOW:
            result = None
            if search_id == MEDIA_TYPE_MOVIE:
                title = "MOVIES"
                result = player.get_movie_list(1000, 3)
            elif search_id == MEDIA_TYPE_TVSHOW:
                title = "TV SHOW"
                result = player.get_movie_list(1000, 4)
            else:
                result = player.get_collection_list(search_id)

            if result is not None and result.get("data"):
                child_media_class = MEDIA_CLASS_MOVIE
                if result.get("type"):
                    child_media_class = MOVIE_TYPE_MEDIA_CLASS[result["type"] + 1]
                children = []
                for item in result["data"]:
                    child_type = item["type"]
                    item_id = item["id"]
                    item_type = search_type
                    # item_thumbnail = None
                    item_thumbnail = entity.get_browse_image_url(item_type, item_id)

                    children.append(
                        BrowseMedia(
                            title=item["name"],
                            media_class=media_class,
                            media_content_id=str(item_id),
                            media_content_type=item_type,
                            can_play=child_type in {1, 5, 6},
                            can_expand=child_type in {3, 4},
                            thumbnail=item_thumbnail,
                        )
                    )
                if result.get("name"):
                    title = result.get("name")

        if children is None:
            raise BrowseError(f"Media not found: {search_type} / {search_id}")

        return BrowseMedia(
            title=title,
            media_class=media_class,
            children_media_class=child_media_class,
            media_content_id=search_id,
            media_content_type=search_type,
            can_play=False,
            children=children,
            can_expand=True,
        )

    def library_payload(player):
        """Create response payload to describe contents of library."""
        library_info = {
            "title": "Zidoo Library",
            "media_class": MEDIA_CLASS_DIRECTORY,
            "media_content_id": "library",
            "media_content_type": "library",
            "can_play": False,
            "can_expand": True,
            "children": [],
        }

        # Add favorite
        for item in FAVORITES:
            library_info["children"].append(
                BrowseMedia(
                    title=item["name"],
                    media_class=MEDIA_CLASS_DIRECTORY,
                    media_content_id=item["path"],
                    media_content_type="file",
                    can_play=False,
                    can_expand=True,
                )
            )

        # Add Movies
        library_info["children"].append(
            BrowseMedia(
                title="MOVIES",
                media_class=MEDIA_CLASS_MOVIE,
                media_content_id=MEDIA_TYPE_MOVIE,
                media_content_type=MEDIA_TYPE_MOVIE,
                can_play=False,
                can_expand=True,
            )
        )
        # Add TV
        library_info["children"].append(
            BrowseMedia(
                title="TV SHOWS",
                media_class=MEDIA_CLASS_TV_SHOW,
                media_content_id=MEDIA_TYPE_TVSHOW,
                media_content_type=MEDIA_TYPE_TVSHOW,
                can_play=False,
                can_expand=True,
            )
        )

        result = player.get_device_list()

        if result is not None and result.get("devices"):

            for item in result["devices"]:
                content_type = item["type"]
                item_type = None
                if content_type is not None and content_type in CONTENT_ITEM_TYPE:
                    item_type = CONTENT_ITEM_TYPE[content_type]
                if item_type is not None:
                    child_media_class = ITEM_TYPE_MEDIA_CLASS[item_type]
                    item_thumbnail = None

                    library_info["children"].append(
                        BrowseMedia(
                            title=item["name"],
                            media_class=child_media_class,
                            media_content_id=item["path"],
                            media_content_type=item_type,
                            can_play=False,
                            can_expand=child_media_class == MEDIA_CLASS_DIRECTORY,
                            thumbnail=item_thumbnail,
                        )
                    )

        response = BrowseMedia(**library_info)
        return response

    if media_content_type in [None, "library"]:
        return library_payload(entity._player)

    payload = {
        "search_type": media_content_type,
        "search_id": media_content_id,
    }

    return build_item_response(entity._player, payload)
