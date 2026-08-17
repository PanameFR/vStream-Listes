import xbmc
import xbmcaddon

_ADDON_ID = xbmcaddon.Addon().getAddonInfo("id")


def _debug_enabled():
    try:
        return xbmcaddon.Addon().getSettingBool("debug_logging")
    except (AttributeError, TypeError):
        return False


def debug(message):
    if _debug_enabled():
        xbmc.log("[%s] %s" % (_ADDON_ID, message), xbmc.LOGINFO)


def error(message):
    xbmc.log("[%s] %s" % (_ADDON_ID, message), xbmc.LOGERROR)
