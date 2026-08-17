"""
Builds a standard Kodi add-on repository (addons.xml + addons.xml.md5 + a
repo/ folder of per-addon zips) out of the addon source folders in this
project, mirroring how vStream's own repository.vstream / venom-xbmc-addons
are published:
  - repository.vstreamlists's addon.xml points at raw.githubusercontent.com
    URLs of addons.xml / addons.xml.md5 / repo/ for the actual auto-update
    checks (no GitHub Pages involved there).
  - This same output, once pushed, is also served via GitHub Pages so Kodi's
    file manager can browse it in HTML to install the first (bootstrap) zip.

Run from anywhere: python tools/build_repo.py
Output is written to <repo_root>/addons.xml, addons.xml.md5 and repo/.
"""
import hashlib
import os
import re
import shutil
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADDON_IDS = ["plugin.video.vstreamlists", "repository.vstreamlists"]
OUTPUT_DIR = os.path.join(ROOT, "repo")

# Files/folders never shipped inside an addon zip.
EXCLUDE_NAMES = {"__pycache__", ".git", ".gitignore", "lists.db"}
EXCLUDE_EXT = {".pyc", ".pyo"}


def read_addon_xml(addon_dir):
    with open(os.path.join(addon_dir, "addon.xml"), "r", encoding="utf-8") as f:
        content = f.read()
    # Strip the XML declaration line first - it has its own version="1.0"
    # attribute that must not be confused with the addon's own version.
    body = re.sub(r"^\s*<\?xml[^>]*\?>\s*", "", content, count=1).strip()
    opening_tag = re.search(r"<addon\b.*?>", body, re.DOTALL).group(0)
    version = re.search(r'version="([^"]+)"', opening_tag).group(1)
    return version, body


def zip_addon(addon_id, addon_dir, version, dest_dir):
    zip_path = os.path.join(dest_dir, "%s-%s.zip" % (addon_id, version))
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for base, dirs, files in os.walk(addon_dir):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_NAMES]
            for name in files:
                if name in EXCLUDE_NAMES or os.path.splitext(name)[1] in EXCLUDE_EXT:
                    continue
                full = os.path.join(base, name)
                rel = os.path.relpath(full, ROOT)  # keeps "<addon_id>/..." as the zip's internal root
                zf.write(full, rel)
    return zip_path


def build_directory_listing(dir_path, title, entries):
    """entries: list of (label, href) shown as plain links so Kodi's file
    manager (which parses <a href> in HTML) can browse and install a zip.
    """
    links = "\n".join('<li><a href="%s">%s</a></li>' % (href, label) for label, href in entries)
    html = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>%s</title></head>
<body><h1>%s</h1><ul>
%s
</ul></body></html>
""" % (title, title, links)
    with open(os.path.join(dir_path, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)


def update_readme_badges(versions):
    """Keeps the version badges in README.md in sync with addon.xml automatically - these are
    plain hardcoded shields.io URLs, easy to bump one and forget the other by hand."""
    readme_path = os.path.join(ROOT, "README.md")
    if not os.path.isfile(readme_path):
        return
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    badge_labels = {
        "plugin.video.vstreamlists": "vStream%20Listes",
        "repository.vstreamlists": "Repository",
    }
    for addon_id, label in badge_labels.items():
        if addon_id not in versions:
            continue
        content = re.sub(
            r"(img\.shields\.io/badge/%s-)[^-]+(-)" % re.escape(label),
            r"\g<1>%s\g<2>" % versions[addon_id],
            content,
        )

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    if os.path.isdir(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    addon_bodies = []
    repo_index_entries = []
    versions = {}

    for addon_id in ADDON_IDS:
        addon_dir = os.path.join(ROOT, addon_id)
        version, body = read_addon_xml(addon_dir)
        versions[addon_id] = version
        addon_bodies.append(body)

        dest_dir = os.path.join(OUTPUT_DIR, addon_id)
        os.makedirs(dest_dir)

        zip_addon(addon_id, addon_dir, version, dest_dir)

        for extra in ("addon.xml", "icon.png", "icon-v2.png", "fanart.png"):
            src = os.path.join(addon_dir, extra)
            if os.path.isfile(src):
                shutil.copy2(src, dest_dir)

        entries = [
            (name, name)
            for name in sorted(os.listdir(dest_dir))
            if name != "index.html"
        ]
        build_directory_listing(dest_dir, "%s" % addon_id, entries)
        repo_index_entries.append(("%s/" % addon_id, "%s/" % addon_id))

    build_directory_listing(OUTPUT_DIR, "vStream Listes - repo", repo_index_entries)

    addons_xml = "<addons>\n" + "\n".join(addon_bodies) + "\n</addons>\n"
    addons_xml_path = os.path.join(ROOT, "addons.xml")
    with open(addons_xml_path, "w", encoding="utf-8") as f:
        f.write(addons_xml)

    digest = hashlib.md5(addons_xml.encode("utf-8")).hexdigest()
    with open(os.path.join(ROOT, "addons.xml.md5"), "w", encoding="utf-8") as f:
        f.write(digest)

    build_directory_listing(
        ROOT,
        "vStream Listes",
        [("repo/", "repo/"), ("addons.xml", "addons.xml"), ("addons.xml.md5", "addons.xml.md5")],
    )

    update_readme_badges(versions)

    print("Built addons.xml (md5 %s) and repo/ for: %s" % (digest, ", ".join(ADDON_IDS)))


if __name__ == "__main__":
    main()
