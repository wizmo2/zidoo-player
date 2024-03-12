"""Support for media browsing."""
import contextlib

from homeassistant.components import media_source
from homeassistant.components.media_player import (
    BrowseMedia,
    MediaClass,
    MediaType,
)

from homeassistant.helpers.network import is_internal_request

from .const import (
    CONF_SHORTCUT,
    ITEM_TYPE_MEDIA_CLASS,
    MEDIA_TYPE_FILE,
    ZCONTENT_ITEM_TYPE,
    ZDEFAULT_SHORTCUTS,
    ZSHORTCUTS,
)
from .zidooaio import ZVIDEO_FILTER_TYPES, ZMUSIC_SEARCH_TYPES

BROWSE_LIMIT = 1000
ZTITLE = "Zidoo Media"


async def build_item_response(entity, payload):
    """Create response payload for search described by payload."""
    search_id = payload["search_id"]
    search_type = payload["search_type"]
    player = entity.coordinator.player
    is_internal = is_internal_request(entity.hass)

    media_class = ITEM_TYPE_MEDIA_CLASS[search_type]
    child_media_class = None
    children = []
    title = ZTITLE
    thumbnail = None
    result = None

    # File Browser Lists
    if media_class == MediaClass.DIRECTORY:  # file system list
        result = await player.get_file_list(search_id)
    if media_class == MediaClass.URL:  # smb system list
        result = await player.get_host_list(search_id)

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
                        can_expand=item_class == MediaClass.DIRECTORY,
                        thumbnail=item_thumbnail,
                    )
                )

                if child_media_class is None:
                    child_media_class = item_class

    # Music Library Lists
    elif search_type in ZMUSIC_SEARCH_TYPES:
        child_media_class = search_type  # should be class
        if "*" in search_id:
            result = await player.search_music(search_id.replace("*", ""), search_type)
            title = search_id
            # search_id = None
        else:
            if search_id in ZMUSIC_SEARCH_TYPES:
                result = await player.get_music_list(search_type)
                if search_type == MediaType.PLAYLIST:  # convert playlist list
                    result.insert(0, {"name": "PLAYING", "id": "playing"})
                    result = to_array(result)  # playlist convertor
                shortcut = get_shortcut_name(search_id)
                if shortcut:
                    title = shortcut
            else:  # is media id
                child_media_class = MediaType.MUSIC
                thumbnail = get_thumbnail_url(
                    search_type, search_id, entity, is_internal
                )
                result = await player.get_music_list(search_type, search_id)

        if result and result.get("array"):
            can_expand = child_media_class != MediaClass.MUSIC
            for item in result["array"]:
                if item.get("result"):
                    data = item["result"]
                else:
                    data = item
                item_name = data.get("name")
                if item_name is None:
                    item_name = "{} - {}".format(data.get("artist"), data.get("title"))
                item_id = data["id"]
                item_type = child_media_class
                item_thumbnail = get_thumbnail_url(
                    item_type, item_id, entity, is_internal
                )
                if thumbnail:  # Song list
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

            if child_media_class == MediaClass.MUSIC and item:
                if search_type == MediaType.ARTIST:
                    title = item["artist"]
                if search_type == MediaType.ALBUM:
                    title = item["album"]

    # Movie/Poster Library Lists
    else:
        child_media_class = MediaClass.MOVIE
        if "*" in search_id:
            result = to_data_list(
                await player.search_movies(search_id.replace("*", ""), search_type)
            )
            title = search_id
        elif search_id in ZVIDEO_FILTER_TYPES:
            result = await player.get_movie_list(search_id, BROWSE_LIMIT)
            shortcut = get_shortcut_name(search_id)
            if shortcut:
                title = shortcut
        else:
            result = await player.get_collection_list(search_id)

        if result and result.get("data"):
            video_type = result.get("type")
            data = result["data"]
            if video_type:
                if video_type == 4:  # tv show episodes
                    child_media_class = MediaType.TRACK
                    episodes = await player.get_episode_list(search_id)
                    if episodes is not None:
                        data = episodes
                        if data[0].get("parentId") > 0:
                            thumbnail = get_thumbnail_url(
                                MediaType.VIDEO,
                                data[0]["parentId"],
                                entity,
                                is_internal,
                            )
            for item in data:
                child_type = item["type"]
                item_id = item["id"]
                item_type = search_type
                if child_type == 0:
                    item_type = MediaType.VIDEO
                    item_id = item["aggregationId"]
                item_thumbnail = get_thumbnail_url(
                    item_type, item_id, entity, is_internal
                )

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
    """converts the serach response to a data list"""
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
        if item["path"] == path:
            return item["name"]


def get_thumbnail_url(media_content_type, media_content_id, entity, is_internal):
    if is_internal:
        url_path = entity.coordinator.player.generate_image_url(
            media_content_id, media_content_type
        )
    else:
        # url_path = entity.get_browse_image_url(media_content_type,media_content_id)
        """2022.2 fix"""
        url_path = (
            f"/api/media_player_proxy/{entity.entity_id}/browse_media"
            f"/{media_content_type}/{media_content_id}"
        )

    return str(url_path)


def media_source_content_filter(item: BrowseMedia) -> bool:
    """Content filter for media sources."""
    # Filter out cameras using PNG over MJPEG. They don't work in Kodi.
    return True
    return not (
        item.media_content_id.startswith("media-source://camera/")
        and item.media_content_type == "image/png"
    )


async def library_payload(entity):
    """Create response payload to describe contents of library."""
    library_info = {
        "title": "Zidoo Library",
        "media_class": MediaClass.DIRECTORY,
        "media_content_id": "library",
        "media_content_type": "library",
        "can_play": False,
        "can_expand": True,
        "children": [],
    }

    # add favorite
    shortcuts = entity.coordinator._config_entry.options.get(
        CONF_SHORTCUT, ZDEFAULT_SHORTCUTS
    )
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
    result = await entity.coordinator.player.get_device_list()
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

    with contextlib.suppress(media_source.BrowseError):
        item = await media_source.async_browse_media(
            entity.hass, None, content_filter=media_source_content_filter
        )
        # If domain is None, it's overview of available sources
        if item.domain is None:
            library_info["children"].extend(item.children)
        else:
            library_info["children"].append(item)

    response = BrowseMedia(**library_info)
    return response
