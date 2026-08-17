import xbmcgui

from resources.lib.tmdb.client import TmdbClient


def build_list_item(media):
    title = media.get("title") or "?"
    li = xbmcgui.ListItem(label=title)

    info = {
        "title": title,
        "originaltitle": media.get("original_title") or title,
        "plot": media.get("overview") or "",
        "mediatype": "movie" if media.get("media_type") == "movie" else "tvshow",
    }
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
