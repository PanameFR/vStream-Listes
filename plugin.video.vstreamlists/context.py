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

# Temporary unconditional diagnostic logging (not gated by the addon's own
# debug_logging setting, so it shows up as long as Kodi's own debug logging
# is on) - to pin down exactly what context.py sees vs. what the user
# actually clicked, since the fix in 0.1.11 didn't resolve the wrong-item
# reports. Remove once the real cause is confirmed.
xbmc.log(
    "[vstreamlists] context.py captured: path=%r title=%r year=%r dbtype=%r"
    % (_PATH, _TITLE, _YEAR, _DBTYPE),
    xbmc.LOGINFO,
)

from resources.lib.context.handler import run

if __name__ == "__main__":
    run(_PATH, _TITLE, _YEAR, _DBTYPE)
