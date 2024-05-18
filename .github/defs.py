import os

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
from_src = lambda path: os.path.abspath(os.path.join(SRC_DIR, path))

def rel_path(path: str, from_path: str) -> str:
    return os.path.relpath(path, os.path.dirname(from_path))

THEME_DIR = from_src("../themes")
RELEASE_DIR = from_src("../release")
PAGES_DIR = from_src("../generated")
TEMP_DIR = from_src("temp")

FEATURED_ORDERING = from_src("data/featured.txt")
CUSTOM_ORDERING = from_src("data/custom.txt")
REMIXED_ORDERING = from_src("data/remixed.txt")
ICONS_ORDERING = from_src("data/icons.txt")
ICONS_BLACKLIST = from_src("data/icons_blacklist.txt")

README_TEST = ["readme.md", "README.md", "readme.txt", "README.txt"]
REL_PATH = os.path.abspath(os.path.join(SRC_DIR, ".."))

PAGES_ICONS_DIR = os.path.join(PAGES_DIR, "icons")
README_PATH = from_src("../README.md")
INDEX_TEMPLATE = from_src("template/index.template.md")
HEADER_TEMPLATE = from_src("template/header.template.md")
GRID_TEMPLATE = from_src("template/grid.template.html")
ITEM_TEMPLATE = from_src("template/item.template.html")

BGM_ICON_URL = "https://user-images.githubusercontent.com/44569252/194010780-d3659ecd-7348-4e44-a81d-06708a4e9734.png"
BGM_ICON = f"<img src=\"{BGM_ICON_URL}\" width=\"16\" title=\"Custom background music included (Click to download MP3 file)\">"

AUTHOR_ICON_URL = "https://user-images.githubusercontent.com/44569252/194037581-698a5004-8b75-4da6-a63d-b41d541ebde2.png"
AUTHOR_ICON = f"<img src=\"{AUTHOR_ICON_URL}\" width=\"16\" title=\"Search themes by this author (Requires GitHub account)\">"

HAS_ICONPACK_ICON_URL = "https://user-images.githubusercontent.com/44569252/215106002-fbcf1815-8080-447c-94c2-61f161efb503.png"
HAS_ICONPACK_ICON = f"<img src=\"{HAS_ICONPACK_ICON_URL}\" height=\"16\" title=\"This theme contains an icon pack\">"

README_ICON_URL = "https://user-images.githubusercontent.com/44569252/215358455-b6a1348b-8161-40d6-9cc1-cc31720377c4.png"
README_ICON = f"<img src=\"{README_ICON_URL}\" height=\"16\" title=\"README\">"

PREVIEW_ICON = f"<img src=\"{HAS_ICONPACK_ICON_URL}\" height=\"16\" title=\"Show full preview\">"

NB_SPACE = "&nbsp;"
NB_SPACER = NB_SPACE * 2
LB_SPACER = " " + NB_SPACE

_pages = {
    "custom": "Custom Themes",
    "remixed": "Remixed Themes",
    "icons_themes": "Theme Icon Packs",
    "icons_standalone": "Standalone Icon Packs"
}

HEADER_LINKS = {
    "index": ["Index", README_PATH],
    **{name: [text.replace(" ", NB_SPACE), os.path.join(PAGES_DIR, name, "index.md")] for name, text in _pages.items()},
    "contributing": ["Contributing", from_src("../CONTRIBUTING.md")]
}

PAGE_SIZE = 12
THEMES_COLS = 3
ICONS_COLS = 4

MAX_RECENTS = 3

THEMES_COLUMN_WIDTH = 46
ICONS_COLUMN_WIDTH = 64

THEMES_COLUMN_SPANNER = NB_SPACE * THEMES_COLUMN_WIDTH
ICONS_COLUMN_SPANNER = NB_SPACE * ICONS_COLUMN_WIDTH

WARN_GENERATED_FILE = f"""<!--{'\n' * 20}
=================================================================================
---------------------------------------------------------------------------------

██████╗  ██████╗     ███╗   ██╗ ██████╗ ████████╗    ███████╗██████╗ ██╗████████╗
██╔══██╗██╔═══██╗    ████╗  ██║██╔═══██╗╚══██╔══╝    ██╔════╝██╔══██╗██║╚══██╔══╝
██║  ██║██║   ██║    ██╔██╗ ██║██║   ██║   ██║       █████╗  ██║  ██║██║   ██║   
██║  ██║██║   ██║    ██║╚██╗██║██║   ██║   ██║       ██╔══╝  ██║  ██║██║   ██║   
██████╔╝╚██████╔╝    ██║ ╚████║╚██████╔╝   ██║       ███████╗██████╔╝██║   ██║   
╚═════╝  ╚═════╝     ╚═╝  ╚═══╝ ╚═════╝    ╚═╝       ╚══════╝╚═════╝ ╚═╝   ╚═╝   

---------------------------------------------------------------------------------
=================================================================================

                  Note: This file was automatically generated.

            Run `python .github/generate.py` to regenerate the pages.
{'\n' * 20}-->
"""
