import re
import urllib.parse

import xbmcaddon

from resources.lib import log

# The one and only component allowed to know vStream's routing details.
# If a future vStream release changes its parameters, only this file
# should need to change - the database and the GUI never build vStream
# URLs themselves.
#
# Verified against the public source of vStream (Kodi-vStream/venom-xbmc-addons):
#   - plugin.video.vstream/default.py            (dispatcher: site=, function=)
#   - plugin.video.vstream/resources/sites/pastebin.py (site=pastebin)
#
# pastebin.py's showMovies() reads an input parameter "sTmdbId" and, when
# present, filters the paste content down to entries whose own TMDB id
# matches - across ALL Pastebin codes/groups the user has configured in
# vStream (no pasteID needed). For movies, showMovies() only ever builds
# one further hop (function=showHosters) once exactly one match is found,
# and getHosterList() - which showHosters() calls - accepts that same
# idTMDB filter directly, bypassing its own title/year matching entirely
# once an id match is found. So for movies we call showHosters directly:
# one less screen than going through showMovies first. TV shows still go
# through showMovies -> showSerieSaisons, since picking a season/episode
# is unavoidable and isn't something we can (or should) skip.
#
# getHosterList() requires siteUrl to carry sMedia, idTMDB and sTitle (a
# plain dict-access, no default - omitting it raises KeyError there), and
# showHosters() separately requires a top-level sMovieTitle parameter for
# display. We never see, choose or store a Pastebin server, code or link
# ourselves - vStream keeps doing all of that.

VSTREAM_ADDON_ID = "plugin.video.vstream"
VSTREAM_PLUGIN_URL = "plugin://%s/" % VSTREAM_ADDON_ID
PASTEBIN_SITE_IDENTIFIER = "pastebin"

_MEDIA_TYPE_TO_SMEDIA = {"movie": "film", "tv": "serie"}
# vStream also has "anime", which - like "serie" - goes through season/
# episode navigation (showSerieSaisons), so we treat it as "tv" when
# reading it back from a vStream item.
_SMEDIA_TO_MEDIA_TYPE = {"film": "movie", "serie": "tv", "anime": "tv"}

_TMDB_ID_RE = re.compile(r"(?:sTmdbId|idTMDB)=(\d+)")
_SMEDIA_RE = re.compile(r"sMedia=([a-zA-Z]+)")


class VStreamPastebinAdapter(object):
    """Only bridge between our extension and vStream. It builds vStream
    plugin:// URLs and reads vStream ListItem paths; it never touches
    vStream's files, settings or database.
    """

    def is_vstream_installed(self):
        try:
            xbmcaddon.Addon(VSTREAM_ADDON_ID)
            return True
        except RuntimeError:
            return False

    def get_vstream_version(self):
        try:
            return xbmcaddon.Addon(VSTREAM_ADDON_ID).getAddonInfo("version")
        except RuntimeError:
            return None

    def check_compatibility(self):
        """Best-effort check. Must never delete or hide any list - at
        worst it lets the caller show a warning before attempting playback.
        """
        if not self.is_vstream_installed():
            return False, "vStream n'est pas installe."
        return True, None

    # ---- reading vStream/Pastebin items (context menu) -----------------

    def is_vstream_item(self, path):
        return bool(path) and VSTREAM_ADDON_ID in path

    def is_pastebin_item(self, path):
        if not self.is_vstream_item(path):
            return False
        unquoted = urllib.parse.unquote(path)
        return ("site=%s" % PASTEBIN_SITE_IDENTIFIER) in unquoted

    def extract_tmdb_id(self, path):
        if not path:
            return None
        unquoted = urllib.parse.unquote(path)
        match = _TMDB_ID_RE.search(unquoted)
        return int(match.group(1)) if match else None

    def extract_media_type(self, path):
        if not path:
            return None
        unquoted = urllib.parse.unquote(path)
        match = _SMEDIA_RE.search(unquoted)
        if not match:
            return None
        return _SMEDIA_TO_MEDIA_TYPE.get(match.group(1))

    # ---- building vStream URLs ------------------------------------------

    def build_vstream_url(self, function, **params):
        query = {"site": PASTEBIN_SITE_IDENTIFIER, "function": function}
        query.update({k: v for k, v in params.items() if v is not None})
        return VSTREAM_PLUGIN_URL + "?" + urllib.parse.urlencode(query)

    @staticmethod
    def _sanitize_title(title):
        # Mirrors pastebin.py's own convention for embedding a title inside
        # one of these nested query strings (it does the same replace
        # before appending '&sTitle=' to a siteUrl it builds itself).
        title = title or ""
        return title.replace("+", " ").replace(" & ", " | ")

    def movie_url(self, tmdb_id, title=None, poster_url=None):
        title = self._sanitize_title(title)
        # siteUrl must contain a '&' for pastebin.py to split it into a
        # prefix (unused) and a params dict. sTitle must be present (even
        # if idTMDB ends up matching and its value is therefore unused for
        # filtering) since getHosterList() accesses aParams['sTitle']
        # directly. Everything about which Pastebin codes to search is
        # left entirely to vStream's own configuration.
        site_url = "vstreamlists&sMedia=film&idTMDB=%s&sTitle=%s" % (tmdb_id, title)
        url = self.build_vstream_url(
            "showHosters", siteUrl=site_url, sMovieTitle=title, sThumb=poster_url
        )
        log.debug("built vStream route: media_type=movie tmdb_id=%s url=%s" % (tmdb_id, url))
        return url

    def tvshow_url(self, tmdb_id):
        # Series still need a season/episode picked by the user, so we
        # only get them as far as vStream's own filtered show listing.
        site_url = "vstreamlists&sMedia=serie"
        url = self.build_vstream_url(
            "showMovies", siteUrl=site_url, sTmdbId=str(tmdb_id)
        )
        log.debug("built vStream route: media_type=tv tmdb_id=%s url=%s" % (tmdb_id, url))
        return url
