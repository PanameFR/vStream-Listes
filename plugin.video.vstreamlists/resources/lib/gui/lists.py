import urllib.parse

import xbmcgui
import xbmcplugin

from resources.lib.gui.media import build_list_item
from resources.lib.adapters.vstream import VStreamPastebinAdapter


def _url(base_url, **params):
    return base_url + "?" + urllib.parse.urlencode(params)


def render(base_url, handle, list_id, lists_manager):
    xbmcplugin.setContent(handle, "videos")

    adapter = VStreamPastebinAdapter()
    vstream_ok, vstream_error = adapter.check_compatibility()

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

        if vstream_ok:
            # Point the item straight at vStream's own directory - Kodi
            # navigates into it natively, no redirect through our plugin.
            target_url = adapter.movie_url(tmdb_id) if media_type == "movie" else adapter.tvshow_url(tmdb_id)
            play_command = "Container.Update(%s)" % target_url
        else:
            # No vStream installed: keep the item local and only surface
            # the warning when the user actually tries to play something.
            target_url = _url(base_url, action="open", **common)
            play_command = "RunPlugin(%s)" % target_url

        commands = [
            ("Lire avec vStream / Pastebin", play_command),
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

        # When vStream is missing, the item's own URL runs our "open"
        # action as a plain (non-directory) invocation - same pattern as
        # the "+ Ajouter..." entries above - so it just shows the warning
        # instead of leaving Kodi waiting on a directory listing.
        xbmcplugin.addDirectoryItem(handle, target_url, li, isFolder=vstream_ok)

    xbmcplugin.endOfDirectory(handle)
