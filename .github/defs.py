import os

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
from_src = lambda path: os.path.join(SRC_DIR, path)

THEME_DIR = from_src("../themes")
RELEASE_DIR = from_src("../release")
TEMP_DIR = from_src("temp")

FEATURED_ORDERING = from_src("data/featured.txt")
CUSTOM_ORDERING = from_src("data/custom.txt")
REMIXED_ORDERING = from_src("data/remixed.txt")
ICONS_ORDERING = from_src("data/icons.txt")
