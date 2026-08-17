import urllib.parse

import xbmcplugin

from resources.lib.adapters.vstream import VStreamPastebinAdapter
from resources.lib.gui.media import enrich_list_item


def _url(base_url, **params):
    params = {k: v for k, v in params.items() if v is not None}
    return base_url + "?" + urllib.parse.urlencode(params)


def render(base_url, handle, listing, query, tmdb_client=None, media_manager=None, cache_ttl=0):
    """Renders a search's results as a plain Kodi directory - nothing here is saved anywhere:
    it exists only for this one listing, exactly like browsing vStream itself would. Adding an
    item to one of the user's own lists is still available per-item (see the context menu
    added below), but the results themselves aren't a list and leave nothing behind once the
    user navigates away.

    vStream's own Pastebin listing items carry only a bare title (no plot, poster or rating -
    see vstream_bridge's docstring), so when a result's TMDB id can be read from its own URL,
    it's enriched in place from our TMDB cache before being added."""
    xbmcplugin.setContent(handle, "videos")
    xbmcplugin.setPluginCategory(handle, 'Recherche Pastebin : "%s"' % query if query else "Recherche Pastebin")

    adapter = VStreamPastebinAdapter()
    for item_url, list_item, is_folder in listing:
        tmdb_id = adapter.extract_tmdb_id(item_url)
        media_type = adapter.extract_media_type(item_url)
        if tmdb_id and media_type:
            smedia = adapter.extract_smedia(item_url)
            add_url = _url(
                base_url,
                action="add_search_result",
                media_type=media_type,
                tmdb_id=tmdb_id,
                smedia=smedia,
            )
            # replaceItems defaults to False: this only adds to whatever context items vStream
            # itself may already have put on the item, it doesn't remove them.
            list_item.addContextMenuItems([("Ajouter a une liste", "RunPlugin(%s)" % add_url)])

            if tmdb_client is not None and tmdb_client.has_api_key() and media_manager is not None:
                media = media_manager.ensure_cached(tmdb_client, media_type, tmdb_id, cache_ttl)
                if media:
                    enrich_list_item(list_item, media)

        xbmcplugin.addDirectoryItem(handle, item_url, list_item, isFolder=is_folder)

    if not listing:
        xbmcplugin.endOfDirectory(handle, succeeded=False, cacheToDisc=False)
        return

    xbmcplugin.endOfDirectory(handle, cacheToDisc=False)
