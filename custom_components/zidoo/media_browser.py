"""Support for media browsing."""
from homeassistant.components.media_player import BrowseError, BrowseMedia
from homeassistant.components.media_player.const import (
    MEDIA_CLASS_ALBUM,
    MEDIA_CLASS_DIRECTORY,
    MEDIA_CLASS_MOVIE,
    MEDIA_CLASS_URL,
    MEDIA_CLASS_MUSIC,
    MEDIA_TYPE_PLAYLIST,
    MEDIA_TYPE_TRACK,
    MEDIA_TYPE_VIDEO,
    MEDIA_TYPE_MUSIC,
    MEDIA_TYPE_ALBUM,
    MEDIA_TYPE_ARTIST,
)
from .const import (
    MEDIA_TYPE_FILE,
    ZTYPE_MEDIA_CLASS,
    ZCONTENT_ITEM_TYPE,
    ITEM_TYPE_MEDIA_CLASS,
    ZSHORTCUTS,
    ZDEFAULT_SHORTCUTS,
    CONF_SHORTCUT,
)
from .zidoorc import ZVIDEO_FILTER_TYPES, ZVIDEO_SEARCH_TYPES, ZMUSIC_SEARCH_TYPES

BROWSE_LIMIT = 1000
ZTITLE = "Zidoo Media"

def browse_media(  # noqa: C901
    entity, is_internal, media_content_type=None, media_content_id=None
):
    """Implement the websocket media browsing helper."""

    def build_item_response(player, payload):
        """Create response payload for search described by payload."""
        search_id = payload["search_id"]
        search_type = payload["search_type"]

        media_class = ITEM_TYPE_MEDIA_CLASS[search_type]
        child_media_class = None
        children = []
        title = ZTITLE
        thumbnail = None
        result = None

        # Universal Search
        if search_id == "*":
            if entity._search_query:
                search_id = search_id + entity._search_query
                if entity._search_type:
                    search_type = entity._search_type
                    child_media_class = search_type
            else:
                raise BrowseError(f"Use Search service to set keyword query string")

        # File Browser Lists
        if media_class == MEDIA_CLASS_DIRECTORY: # file system list
            result = player.get_file_list(search_id)
        if media_class == MEDIA_CLASS_URL: # smb system list
            result = player.get_host_list(search_id)

        if result is not None and result.get("filelist"):
            for item in result["filelist"]:
                content_type = item["type"]
                item_type = None
                if content_type is not None and content_type in ZCONTENT_ITEM_TYPE:
                    item_type = ZCONTENT_ITEM_TYPE[content_type]
                if item_type is not None:
                    item_class = ITEM_TYPE_MEDIA_CLASS[item_type]
                    item_thumbnail = None

                    children.append(
                        BrowseMedia(
                            title=item["name"],
                            media_class=item_class,
                            media_content_id=item["path"],
                            media_content_type=MEDIA_TYPE_FILE,
                            can_play=True,
                            can_expand=item_class == MEDIA_CLASS_DIRECTORY,
                            thumbnail=item_thumbnail,
                        )
                    )

                    if child_media_class is None:
                        child_media_class = item_class

        # Music Library Lists
        elif search_type in ZMUSIC_SEARCH_TYPES:
            child_media_class = search_type # should be class
            if "*" in search_id:
                result = player.search_music(search_id.replace("*",""), search_type)
                title = search_id
                # search_id = None
            else:
                if search_id in ZMUSIC_SEARCH_TYPES:
                    result = player.get_music_list(search_type)
                    if search_type == MEDIA_TYPE_PLAYLIST: # convert playlist list
                        result.insert(0,{"name":"PLAYING","id":"playing"})
                        result = to_array(result) # playlist convertor
                    shortcut = get_shortcut_name(search_id)
                    if shortcut: title = shortcut
                else: # is media id
                    child_media_class=MEDIA_TYPE_MUSIC
                    thumbnail = get_thumbnail_url(search_type, search_id)
                    result = player.get_music_list(search_type, search_id)

            if result and result.get("array"):
                can_expand = (child_media_class!=MEDIA_CLASS_MUSIC)
                for item in result["array"]:
                    if item.get("result"):
                        data = item["result"]
                    else:
                        data = item
                    item_name = data.get("name")
                    if item_name is None:
                        item_name = "{} - {}".format(data.get("artist"),data.get("title"))
                    item_id = data["id"]
                    item_type = child_media_class
                    item_thumbnail = get_thumbnail_url(item_type, item_id)
                    if thumbnail: # Song list
                        item_id = "{},{}".format(search_id, item_id)

                    children.append(
                        BrowseMedia(
                            title=item_name,
                            media_class=media_class,
                            media_content_id=str(item_id),
                            media_content_type=search_type,
                            can_play=True,
                            can_expand=can_expand,
                            thumbnail=item_thumbnail,
                        )
                    )

        # Movie/Poster Library Lists
        else:
            child_media_class = MEDIA_CLASS_MOVIE
            if "*" in search_id:
                result = to_data_list(
                    player.search_movies(search_id.replace("*",""), search_type)
                )
                title = search_id
            elif search_id in ZVIDEO_FILTER_TYPES:
                result = player.get_movie_list(search_id, BROWSE_LIMIT)
                shortcut = get_shortcut_name(search_id)
                if shortcut: title = shortcut
            else:
                result = player.get_collection_list(search_id)

            if result and result.get("data"):
                video_type = result.get("type")
                data = result["data"]
                if video_type:
                    if video_type == 4: # tv show episodes
                        child_media_class = MEDIA_TYPE_TRACK
                        episodes = player.get_episode_list(search_id)
                        if episodes is not None:
                            data = episodes
                            if data[0].get("parentId") > 0:
                                thumbnail = get_thumbnail_url(MEDIA_TYPE_VIDEO, data[0]["parentId"])
                for item in data:
                    child_type = item["type"]
                    item_id = item["id"]
                    item_type = search_type
                    if child_type == 0:
                        item_type = MEDIA_TYPE_VIDEO
                        item_id = item["aggregationId"]
                    item_thumbnail = get_thumbnail_url(item_type, item_id)

                    children.append(
                        BrowseMedia(
                            title=item["name"],
                            media_class=media_class,
                            media_content_id=str(item_id),
                            media_content_type=item_type,
                            can_play=child_type in {1, 5, 6},
                            can_expand=child_type in {2, 3, 4, 6},
                            thumbnail=item_thumbnail,
                        )
                    )
                if result.get("name"):
                    title = result["name"]

        return BrowseMedia(
            title=title,
            media_class=media_class,
            children_media_class=child_media_class,
            media_content_id=search_id,
            media_content_type=search_type,
            can_play=(thumbnail is not None),
            children=children,
            can_expand=True,
            thumbnail=thumbnail,
        )

    def to_data_list(response):
        """ converts the serach response to a data list"""
        data_list = []
        if response and response.get("all"):
            for item in response["all"]:
                data_list.append(item["aggregation"])
        elif response and response.get("tvs"):
            for item in response["tvs"]:
                data_list.append(item["aggregation"])
        elif response and response.get("movies"):
            for item in response["movies"]:
                data_list.append(item["aggregation"])
        elif response and response.get("collections"):
            for item in response["collections"]:
                data_list.append(item["aggregation"])

        if data_list:
            return_value = {}
            return_value["name"] = response["key"]
            return_value["data"] = data_list

            return return_value

    def to_array(response):
        return_value = {}
        return_value["array"] = response
        return return_value

    def get_shortcut_name(path):
        for item in ZSHORTCUTS:
            if item["path"] == path: return item["name"]

    def get_thumbnail_url(media_content_type, media_content_id):
        if is_internal:
            url_path = entity._player.generate_image_url(media_content_id, media_content_type)
        else:
            url_path = entity.get_browse_image_url(media_content_type,media_content_id)
            """ 2022.2 fix
            url_path = (
                f"/api/media_player_proxy/{entity.entity_id}/browse_media"
                f"/{media_content_type}/{media_content_id}"
            ) """

        return str(url_path)

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

        # add favorite
        shortcuts = entity._config_entry.options.get(CONF_SHORTCUT, ZDEFAULT_SHORTCUTS)
        for item in ZSHORTCUTS:
            if item["path"] in shortcuts:
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

        # add zidoo file devices
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
