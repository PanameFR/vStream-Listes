import sys
import urllib.parse

import xbmc
import xbmcaddon

from resources.lib.database.manager import DatabaseManager
from resources.lib.lists.manager import ListsManager
from resources.lib.media.manager import MediaManager
from resources.lib.tmdb.client import TmdbClient
from resources.lib.adapters.vstream import VStreamPastebinAdapter
from resources.lib.adapters import vstream_bridge
from resources.lib.gui import home, lists as lists_gui, search as search_gui, dialogs
from resources.lib import log

ADDON = xbmcaddon.Addon()
BASE_URL = sys.argv[0]
HANDLE = int(sys.argv[1])
PARAMS = dict(urllib.parse.parse_qsl(sys.argv[2][1:])) if len(sys.argv) > 2 else {}

DB = DatabaseManager("special://profile/addon_data/%s/" % ADDON.getAddonInfo("id"))
LISTS = ListsManager(DB)
MEDIA = MediaManager(DB)


def _tmdb_client():
    api_key = ADDON.getSetting("tmdb_api_key")
    language = ADDON.getSetting("metadata_language") or "fr-FR"
    return TmdbClient(api_key, language=language)


def _cache_ttl_seconds():
    try:
        hours = int(ADDON.getSetting("cache_duration") or "72")
    except ValueError:
        hours = 72
    return hours * 3600


def _show_count():
    try:
        return ADDON.getSettingBool("show_item_count")
    except (AttributeError, TypeError):
        return True


def _refresh():
    xbmc.executebuiltin("Container.Refresh")


def _int(value):
    return int(value) if value is not None else None


# ---- list management ---------------------------------------------------


def action_create_list():
    name = dialogs.ask_text("Nom de la nouvelle liste")
    if name:
        try:
            LISTS.create_list(name)
        except ValueError:
            dialogs.notify("vStream Listes", "Le nom ne peut pas etre vide")
    _refresh()


def action_rename_list():
    list_id = _int(PARAMS.get("list_id"))
    current = LISTS.get_list(list_id)
    if not current:
        return
    name = dialogs.ask_text("Renommer la liste", default=current["name"])
    if name:
        LISTS.rename_list(list_id, name)
    _refresh()


def action_delete_list():
    list_id = _int(PARAMS.get("list_id"))
    current = LISTS.get_list(list_id)
    if not current:
        return
    if dialogs.confirm("Supprimer la liste", 'Supprimer la liste "%s" ?' % current["name"]):
        LISTS.delete_list(list_id)
    _refresh()


def action_move_list():
    LISTS.move_list(_int(PARAMS.get("list_id")), PARAMS.get("direction"))
    _refresh()


# ---- media in a list -----------------------------------------------------


def action_remove_item():
    LISTS.remove_item(
        _int(PARAMS.get("list_id")), PARAMS.get("media_type"), _int(PARAMS.get("tmdb_id"))
    )
    _refresh()


def action_reorder_item():
    LISTS.move_item_position(
        _int(PARAMS.get("list_id")),
        PARAMS.get("media_type"),
        _int(PARAMS.get("tmdb_id")),
        PARAMS.get("direction"),
    )
    _refresh()


def action_move_item():
    list_id = _int(PARAMS.get("list_id"))
    media_type = PARAMS.get("media_type")
    tmdb_id = _int(PARAMS.get("tmdb_id"))

    target = dialogs.choose_list(LISTS.get_lists(), heading="Deplacer vers", exclude_list_id=list_id)
    if target is None:
        return
    if target == "__create__":
        name = dialogs.ask_text("Nom de la nouvelle liste")
        if not name:
            return
        target = LISTS.create_list(name)

    LISTS.move_item(list_id, target, media_type, tmdb_id)
    _refresh()


def action_copy_item():
    list_id = _int(PARAMS.get("list_id"))
    media_type = PARAMS.get("media_type")
    tmdb_id = _int(PARAMS.get("tmdb_id"))

    target = dialogs.choose_list(
        LISTS.get_lists(), heading="Ajouter a une autre liste", exclude_list_id=list_id
    )
    if target is None:
        return
    if target == "__create__":
        name = dialogs.ask_text("Nom de la nouvelle liste")
        if not name:
            return
        target = LISTS.create_list(name)

    LISTS.add_item(target, media_type, tmdb_id)
    _refresh()


def action_search_pastebin_prompt():
    query = dialogs.ask_text("Rechercher dans Pastebin (tous medias)")
    if query:
        url = "%s?%s" % (BASE_URL, urllib.parse.urlencode({"action": "search_pastebin", "query": query}))
        xbmc.executebuiltin("Container.Update(%s)" % url)


def action_add_search_result():
    media_type = PARAMS.get("media_type")
    tmdb_id = _int(PARAMS.get("tmdb_id"))
    smedia = PARAMS.get("smedia")

    target = dialogs.choose_list(LISTS.get_lists(), heading="Ajouter a une liste")
    if target is None:
        return
    if target == "__create__":
        name = dialogs.ask_text("Nom de la nouvelle liste")
        if not name:
            return
        target = LISTS.create_list(name)

    LISTS.add_item(target, media_type, tmdb_id)

    client = _tmdb_client()
    if client.has_api_key():
        MEDIA.ensure_cached(client, media_type, tmdb_id, 0)
    # Separate from ensure_cached's TMDB-sourced upsert so a missing API
    # key or an unreachable TMDB never blocks remembering which vStream
    # category (film/serie/anime/divers) this title came from.
    MEDIA.set_smedia(media_type, tmdb_id, smedia)

    dialogs.notify("vStream Listes", "Ajoute.")


def action_refresh_metadata():
    media_type = PARAMS.get("media_type")
    tmdb_id = _int(PARAMS.get("tmdb_id"))
    client = _tmdb_client()
    try:
        fresh = client.refresh_metadata(media_type, tmdb_id)
        if fresh:
            MEDIA.upsert(fresh)
    except Exception:
        dialogs.notify("vStream Listes", "TMDB est actuellement inaccessible")
    _refresh()


def action_open():
    # Reached only when vStream wasn't installed at render time (the list
    # otherwise points items straight at vStream's own directory - see
    # gui/lists.py). Re-check in case that has changed since.
    media_type = PARAMS.get("media_type")
    tmdb_id = _int(PARAMS.get("tmdb_id"))
    title = PARAMS.get("title")
    smedia = PARAMS.get("smedia")

    adapter = VStreamPastebinAdapter()
    ok, message = adapter.check_compatibility()
    if not ok:
        dialogs.notify("vStream Listes", message)
    else:
        if media_type == "movie":
            url = adapter.movie_url(tmdb_id, title=title)
        else:
            url = adapter.tvshow_url(tmdb_id, title=title, smedia=smedia)
        xbmc.executebuiltin("Container.Update(%s)" % url)


# ---- directory rendering --------------------------------------------------


def render_home():
    home.render(BASE_URL, HANDLE, LISTS, show_count=_show_count())


def render_list():
    list_id = _int(PARAMS.get("list_id"))
    ttl = _cache_ttl_seconds()
    client = _tmdb_client()
    if client.has_api_key():
        for item in LISTS.get_items(list_id):
            MEDIA.ensure_cached(client, item["media_type"], item["tmdb_id"], ttl)
    lists_gui.render(BASE_URL, HANDLE, list_id, LISTS)


def render_search():
    query = PARAMS.get("query")
    if not query:
        dialogs.notify("vStream Listes", "Recherche vide.")
        search_gui.render(BASE_URL, HANDLE, [], query)
        return
    try:
        listing = vstream_bridge.search_all_categories(query)
    except RuntimeError as exc:
        dialogs.notify("vStream Listes", str(exc))
        search_gui.render(BASE_URL, HANDLE, [], query)
        return
    except Exception as exc:
        log.error("render_search: unexpected failure: %s" % exc)
        dialogs.notify("vStream Listes", "La recherche Pastebin a echoue.")
        search_gui.render(BASE_URL, HANDLE, [], query)
        return
    search_gui.render(BASE_URL, HANDLE, listing, query)


ACTIONS = {
    None: render_home,
    "create_list": action_create_list,
    "rename_list": action_rename_list,
    "delete_list": action_delete_list,
    "move_list": action_move_list,
    "show_list": render_list,
    "search_pastebin_prompt": action_search_pastebin_prompt,
    "search_pastebin": render_search,
    "add_search_result": action_add_search_result,
    "remove_item": action_remove_item,
    "reorder_item": action_reorder_item,
    "move_item": action_move_item,
    "copy_item": action_copy_item,
    "refresh_metadata": action_refresh_metadata,
    "open": action_open,
}


def main():
    action = PARAMS.get("action")
    handler = ACTIONS.get(action)
    if handler is None:
        render_home()
        return
    handler()


if __name__ == "__main__":
    main()
