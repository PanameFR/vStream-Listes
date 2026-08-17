import urllib.parse

import xbmcgui
import xbmcplugin


def _url(base_url, **params):
    return base_url + "?" + urllib.parse.urlencode(params)


def render(base_url, handle, lists_manager, show_count=True):
    xbmcplugin.setContent(handle, "videos")

    li = xbmcgui.ListItem(label="+ Creer une liste")
    li.setArt({"icon": "DefaultAddSource.png"})
    xbmcplugin.addDirectoryItem(
        handle, _url(base_url, action="create_list"), li, isFolder=False
    )

    for lst in lists_manager.get_lists():
        label = lst["name"]
        if show_count:
            label = "%s   [COLOR grey](%d)[/COLOR]" % (label, lst["item_count"])

        li = xbmcgui.ListItem(label=label)
        li.setArt({"icon": "DefaultVideoPlaylists.png"})

        commands = [
            (
                "Renommer",
                "RunPlugin(%s)" % _url(base_url, action="rename_list", list_id=lst["id"]),
            ),
            (
                "Supprimer",
                "RunPlugin(%s)" % _url(base_url, action="delete_list", list_id=lst["id"]),
            ),
            (
                "Monter",
                "RunPlugin(%s)"
                % _url(base_url, action="move_list", list_id=lst["id"], direction="up"),
            ),
            (
                "Descendre",
                "RunPlugin(%s)"
                % _url(base_url, action="move_list", list_id=lst["id"], direction="down"),
            ),
            (
                "Mettre en premier",
                "RunPlugin(%s)"
                % _url(base_url, action="move_list", list_id=lst["id"], direction="first"),
            ),
            (
                "Mettre en dernier",
                "RunPlugin(%s)"
                % _url(base_url, action="move_list", list_id=lst["id"], direction="last"),
            ),
        ]
        li.addContextMenuItems(commands)

        xbmcplugin.addDirectoryItem(
            handle,
            _url(base_url, action="show_list", list_id=lst["id"]),
            li,
            isFolder=True,
        )

    xbmcplugin.endOfDirectory(handle)
