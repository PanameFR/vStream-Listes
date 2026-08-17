import sys
import urllib.parse

import xbmcaddon

from resources.lib import log
from resources.lib.adapters.vstream import VSTREAM_ADDON_ID, VStreamPastebinAdapter

# Reads vStream's own Pastebin search directly (never its files - only its already-installed
# Python modules, imported at runtime) so a search can cover every category (film/serie/anime/
# divers) in one merged list instead of the one-category-at-a-time menu vStream itself offers.
#
# The catch: both addons use the exact same top-level package name "resources" for their own
# code (resources.lib.xxx). Kodi's Python process caches imported modules in sys.modules keyed
# by that name, so a plain "import resources.sites.pastebin" would resolve against whichever
# addon's "resources" is already cached - ours, since we're the ones running. _import_scope()
# below evicts our own "resources.*" entries from sys.modules and puts vStream's addon
# directory first on sys.path for the duration of the import only, then restores everything
# exactly as it was. Once vStream's classes/functions are imported into local variables here,
# calling them later needs none of that - Python function calls don't re-consult sys.modules,
# only fresh "import" statements do.
#
# Fragility this accepts: vStream's showMovies() is a private implementation detail, not a
# published API. If a future vStream release renames it, changes its parameters, or reworks
# how it filters/paginates, this search breaks until updated to match - silently, until
# something calls it. That trade-off is intentional: it's the only way to get one genuinely
# merged list instead of four separate ones, without touching vStream's own files.

_CATEGORIES = ("film", "serie", "anime", "divers")


class _ImportScope:
    """Context manager: temporarily hands the "resources" module namespace to vStream's addon
    directory, then hands it back - see the module docstring above for why."""

    def __enter__(self):
        self._saved_path = list(sys.path)
        self._saved_modules = {}
        for name in list(sys.modules):
            if name == "resources" or name.startswith("resources."):
                self._saved_modules[name] = sys.modules.pop(name)

        vstream_root = xbmcaddon.Addon(VSTREAM_ADDON_ID).getAddonInfo("path")
        sys.path.insert(0, vstream_root)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for name in list(sys.modules):
            if name == "resources" or name.startswith("resources."):
                del sys.modules[name]
        sys.path[:] = self._saved_path
        sys.modules.update(self._saved_modules)
        return False


def search_all_categories(query):
    """Searches vStream's Pastebin sources across every category at once. Returns a list of
    (item_url, xbmcgui.ListItem, is_folder) tuples - the exact shape xbmcplugin.addDirectoryItems
    expects - built entirely by vStream's own code (titles, thumbnails, navigation URLs), so a
    selected item plays or opens exactly as it would from vStream itself.

    Raises RuntimeError with a message safe to show the user if vStream isn't installed or the
    search itself fails.
    """
    ok, message = VStreamPastebinAdapter().check_compatibility()
    if not ok:
        raise RuntimeError(message)

    quoted = urllib.parse.quote(query, safe="")

    with _ImportScope():
        try:
            from resources.sites import pastebin as vstream_pastebin
        except Exception as exc:
            log.error("vstream_bridge: could not import vStream's pastebin module: %s" % exc)
            raise RuntimeError("Impossible de lire le module Pastebin de vStream (vStream a peut-etre change).")

        # Fresh accumulator for this search only - see module docstring: this list is a class
        # attribute shared by every cGui instance, so it must be reset before reusing it, and
        # emptied out completely once we're done reading it (so a plain vStream browse later in
        # the same Kodi session, if the process is reused, doesn't inherit stale entries).
        vstream_pastebin.cGui.listing = []

        for category in _CATEGORIES:
            site_url = "vstreamlists&sMedia=%s&sSearch=%s" % (category, quoted)
            try:
                vstream_pastebin.showMovies(sSearch=site_url)
            except Exception as exc:
                log.error("vstream_bridge: search failed for category '%s': %s" % (category, exc))
                # One category failing (e.g. one Pastebin source unreachable) shouldn't lose
                # results already found in the others.
                continue

        results = list(vstream_pastebin.cGui.listing)
        vstream_pastebin.cGui.listing = []

    return results
