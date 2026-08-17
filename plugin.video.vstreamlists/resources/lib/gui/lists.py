import urllib.parse

import xbmcgui
import xbmcplugin

from resources.lib.gui.media import build_list_item


def _url(base_url, **params):
    return base_url + "?" + urllib.parse.urlencode(params)


def render(base_url, handle, list_id, lists_manager):
    xbmcplugin.setContent(handle, "videos")

    for entry in ("Ajouter un film", "Ajouter une serie"):
        media_type = "movie" if "film" in entry else "tv"
        li = xbmcgui.ListItem(label="+ %s" % entry)
        li.setArt({"icon": "DefaultAddSource.png"})
        xbmcplugin.addDirectoryItem(
            handle,
            _url(base_url, action="add_media", list_id=list_id, media_type=media_type),
            li,
            isFolder=False,
        )

    items = lists_manager.get_items(list_id)
    for item in items:
        media_type = item["media_type"]
        tmdb_id = item["tmdb_id"]

        if item.get("title"):
            li = build_list_item(item)
        else:
            # Metadata not cached yet (e.g. TMDB was unreachable on add).
            li = xbmcgui.ListItem(label="movie/%s" % tmdb_id if media_type == "movie" else "tv/%s" % tmdb_id)

        common = dict(list_id=list_id, media_type=media_type, tmdb_id=tmdb_id)

        commands = [
            (
                "Lire avec vStream / Pastebin",
                "RunPlugin(%s)" % _url(base_url, action="open", **common),
            ),
            (
                "Ajouter a une autre liste",
                "RunPlugin(%s)" % _url(base_url, action="copy_item", **common),
            ),
            (
                "Deplacer vers...",
                "RunPlugin(%s)" % _url(base_url, action="move_item", **common),
            ),
            (
                "Retirer de cette liste",
                "RunPlugin(%s)" % _url(base_url, action="remove_item", **common),
            ),
            (
                "Monter",
                "RunPlugin(%s)" % _url(base_url, action="reorder_item", direction="up", **common),
            ),
            (
                "Descendre",
                "RunPlugin(%s)" % _url(base_url, action="reorder_item", direction="down", **common),
            ),
            (
                "Mettre en premier",
                "RunPlugin(%s)" % _url(base_url, action="reorder_item", direction="first", **common),
            ),
            (
                "Mettre en dernier",
                "RunPlugin(%s)" % _url(base_url, action="reorder_item", direction="last", **common),
            ),
            (
                "Actualiser les informations TMDB",
                "RunPlugin(%s)" % _url(base_url, action="refresh_metadata", **common),
            ),
        ]
        li.addContextMenuItems(commands)

        xbmcplugin.addDirectoryItem(
            handle,
            _url(base_url, action="open", **common),
            li,
            isFolder=True,
        )

    xbmcplugin.endOfDirectory(handle)
