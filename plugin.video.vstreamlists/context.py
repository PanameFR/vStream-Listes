import xbmc

# Read the selected ListItem's identity FIRST, before anything else - even
# resources.lib.context.handler's own imports (sqlite, TMDB client, etc.) take
# enough time to load that the underlying container's focus can drift to a
# different item in the meantime, silently adding the wrong title to a list.
# xbmc itself is always already loaded by Kodi, so this costs nothing extra.
_PATH = xbmc.getInfoLabel("ListItem.FolderPath") or xbmc.getInfoLabel("ListItem.Path")
_TITLE = xbmc.getInfoLabel("ListItem.Title") or xbmc.getInfoLabel("ListItem.Label")
_YEAR = xbmc.getInfoLabel("ListItem.Year")
_DBTYPE = xbmc.getInfoLabel("ListItem.DBTYPE")

from resources.lib.context.handler import run

if __name__ == "__main__":
    run(_PATH, _TITLE, _YEAR, _DBTYPE)
