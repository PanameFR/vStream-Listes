import xbmcgui

from resources.lib.tmdb.client import TmdbClient


def enrich_list_item(li, media):
    """Sets TMDB-sourced info/art (plot, poster, rating...) on an existing
    ListItem, without touching its label - used both for our own list
    items and for vStream's own search-result items, which carry a title
    but no metadata of their own (see gui/search.py).
    """
    title = media.get("title")

    info = {
        "plot": media.get("overview") or "",
        "mediatype": "movie" if media.get("media_type") == "movie" else "tvshow",
    }
    if title:
        info["title"] = title
        info["originaltitle"] = media.get("original_title") or title
    if media.get("year"):
        try:
            info["year"] = int(media["year"])
        except (TypeError, ValueError):
            pass
    if media.get("genres"):
        info["genre"] = media["genres"] if isinstance(media["genres"], list) else [media["genres"]]
    if media.get("runtime"):
        info["duration"] = int(media["runtime"]) * 60
    if media.get("rating") is not None:
        li.setRating("tmdb", float(media["rating"]))

    li.setInfo("video", info)

    art = {}
    poster = TmdbClient.image_url(media.get("poster_path"))
    fanart = TmdbClient.image_url(media.get("backdrop_path"), size="w1280")
    if poster:
        art["poster"] = poster
        art["thumb"] = poster
    if fanart:
        art["fanart"] = fanart
    if art:
        li.setArt(art)

    return li


def build_list_item(media):
    li = xbmcgui.ListItem(label=media.get("title") or "?")
    return enrich_list_item(li, media)
