import xbmcaddon

from resources.lib.database.manager import DatabaseManager
from resources.lib.lists.manager import ListsManager
from resources.lib.media.manager import MediaManager
from resources.lib.tmdb.client import TmdbClient
from resources.lib.adapters.vstream import VStreamPastebinAdapter
from resources.lib.gui import dialogs


def run(path, title, year, dbtype):
    """Entry point for the 'Ajouter a mes listes' context menu item shown
    on vStream/Pastebin entries. Never touches vStream itself.

    path/title/year/dbtype are the selected ListItem's own infolabels, read
    by context.py before anything else - see its comment for why that
    ordering matters (the container's focus can drift while this module's
    own imports are still loading, otherwise).
    """
    adapter = VStreamPastebinAdapter()

    if not adapter.is_pastebin_item(path):
        dialogs.notify("vStream Listes", "Cet element ne provient pas de la source Pastebin de vStream")
        return

    addon = xbmcaddon.Addon()
    db = DatabaseManager("special://profile/addon_data/%s/" % addon.getAddonInfo("id"))
    lists_manager = ListsManager(db)
    media_manager = MediaManager(db)

    media_type = adapter.extract_media_type(path)
    tmdb_id = adapter.extract_tmdb_id(path)

    client = TmdbClient(
        addon.getSetting("tmdb_api_key"),
        language=addon.getSetting("metadata_language") or "fr-FR",
    )

    media = None

    if tmdb_id:
        # ID already known: no ambiguity, add immediately and enrich
        # from TMDB afterwards (best-effort).
        if not media_type:
            media_type = "movie"
        try:
            media = client.refresh_metadata(media_type, tmdb_id)
        except Exception:
            media = {"media_type": media_type, "tmdb_id": tmdb_id, "title": title, "year": year or None}
    else:
        if not title:
            dialogs.notify("vStream Listes", "Impossible d'identifier ce contenu")
            return

        if not media_type:
            media_type = "tv" if dbtype == "tvshow" else "movie"

        if not client.has_api_key():
            dialogs.notify("vStream Listes", "Aucune cle API TMDB configuree")
            return

        try:
            results = (
                client.search_movie(title, year=year or None)
                if media_type == "movie"
                else client.search_tv(title, year=year or None)
            )
        except Exception:
            dialogs.notify("vStream Listes", "TMDB est actuellement inaccessible")
            return

        chosen = dialogs.choose_tmdb_result(results, media_type)
        if not chosen:
            return  # user must pick explicitly, never guess silently
        media = chosen
        tmdb_id = media["tmdb_id"]

    target = dialogs.choose_list(lists_manager.get_lists(), heading="Ajouter a mes listes")
    if target is None:
        return
    if target == "__create__":
        name = dialogs.ask_text("Nom de la nouvelle liste")
        if not name:
            return
        target = lists_manager.create_list(name)

    if media:
        media_manager.upsert(media)
    lists_manager.add_item(target, media_type, tmdb_id)
    dialogs.notify("vStream Listes", "Ajoute a la liste")
