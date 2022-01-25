"""Support for media browsing."""
from homeassistant.components.media_player import BrowseError, BrowseMedia
from homeassistant.components.media_player.const import (
    MEDIA_CLASS_DIRECTORY,
    MEDIA_CLASS_MOVIE,
    MEDIA_CLASS_TV_SHOW,
    MEDIA_CLASS_URL,
    MEDIA_TYPE_MOVIE,
    MEDIA_TYPE_TVSHOW,
)
from .const import MEDIA_TYPE_FILE, ZTYPE_MEDIA_TYPE, ZTYPE_MEDIA_CLASS, ZCONTENT_ITEM_TYPE, ITEM_TYPE_MEDIA_CLASS

BROWSE_LIMIT = 1000

ZITEM_TYPE_FILTER = {
    MEDIA_TYPE_FILE: 0,
    MEDIA_TYPE_MOVIE: 3,
    MEDIA_TYPE_TVSHOW: 4,
}

ZTITLE = "Zidoo Media"

ZFAVORITES = [
    # {"name": "DOWNLOADS", "path": "/tmp/ramfs/mnt/192.168.1.1%23SHARED/DOWNLOAD", "type": MEDIA_TYPE_FILE},
    {"name": "MOVIES", "path": MEDIA_TYPE_MOVIE, "type": MEDIA_TYPE_MOVIE},
    {"name": "TV SHOW", "path": MEDIA_TYPE_TVSHOW, "type": MEDIA_TYPE_TVSHOW},
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
        title = ZTITLE
        thumbnail = None

        if media_class == MEDIA_CLASS_DIRECTORY or media_class == MEDIA_CLASS_URL:
            if media_class == MEDIA_CLASS_DIRECTORY:
                result = player.get_file_list(search_id)
            else:
                result = player.get_host_list(search_id)

            if result is not None and result.get("filelist"):
                children = []
                for item in result["filelist"]:
                    content_type = item["type"]
                    item_type = None
                    if content_type is not None and content_type in ZCONTENT_ITEM_TYPE:
                        item_type = ZCONTENT_ITEM_TYPE[content_type]
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
                result = player.get_movie_list(ZITEM_TYPE_FILTER[search_id], BROWSE_LIMIT)
            elif search_id == MEDIA_TYPE_TVSHOW:
                title = "TV SHOW"
                result = player.get_movie_list(ZITEM_TYPE_FILTER[search_id], BROWSE_LIMIT)
            else:
                result = player.get_collection_list(search_id)

            if result is not None and result.get("data"):
                child_media_class = MEDIA_CLASS_MOVIE
                video_type = result.get("type")
                data = result["data"]
                if video_type:
                    child_media_class = ZTYPE_MEDIA_CLASS[int(video_type) + 1]
                    if video_type == 4 and result.get("size") > 1:
                        # get episodes in sorted order
                        episodes = player.get_episode_list(search_id)
                        if episodes is not None:
                            data = episodes
                    if video_type == 4 and data[0].get("parentId") > 0:
                        thumbnail = player.generate_movie_image_url(data[0]["parentId"])
                children = []
                for item in data:
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
                            can_expand=child_type in {2, 3, 4},
                            thumbnail=item_thumbnail,
                        )
                    )

                if result.get("name"):
                    title = result.get("name")

        # if children is None:
        #    raise BrowseError(f"Media not found: {search_type} / {search_id}")

        return BrowseMedia(
            title=title,
            media_class=media_class,
            children_media_class=child_media_class,
            media_content_id=search_id,
            media_content_type=search_type,
            can_play=False,
            children=children,
            can_expand=True,
            thumbnail=thumbnail
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
        for item in ZFAVORITES:
            library_info["children"].append(
                BrowseMedia(
                    title=item["name"],
                    media_class=ITEM_TYPE_MEDIA_CLASS[item["type"]],
                    media_content_id=item["path"],
                    media_content_type=item["type"],
                    can_play=False,
                    can_expand=True,
                )
            )

        result = player.get_device_list()

        if result is not None:

            for item in result:
                content_type = item["type"]
                item_type = None
                if content_type is not None and content_type in ZCONTENT_ITEM_TYPE:
                    item_type = ZCONTENT_ITEM_TYPE[content_type]
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
                            can_expand=True,
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
