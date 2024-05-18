#!/usr/bin/python3

import os
import json
import math
from typing import Callable
from tqdm import tqdm

from string import Template

from defs import *

from utils import get_files, get_ordering, get_subdirs, urlencode, git_last_changed
from validation import validate_theme
from generate_icons import generate_icon_pack_table, get_ordered_icons


icons_blacklist = get_ordering(ICONS_BLACKLIST)
themes_featured = []
themes_icon_packs = []


def main():
    global themes_featured

    if not os.path.exists(RELEASE_DIR):
        print("No themes released")
        return

    print("Generating READMEs...")

    released_themes = [
        os.path.splitext(file)[0]
        for file in get_files(RELEASE_DIR, "zip")]
    is_released = lambda theme: theme in released_themes

    themes_featured = list(filter(is_released, get_ordering(FEATURED_ORDERING)))

    themes_custom = list(filter(is_released, get_ordering(CUSTOM_ORDERING)))
    themes_custom.reverse()

    themes_remixed = list(filter(is_released, get_ordering(REMIXED_ORDERING)))
    themes_remixed.reverse()

    standalone_icon_packs = get_ordered_icons()

    os.makedirs(PAGES_DIR, exist_ok=True)

    write_pages(themes_custom, "custom", "Custom Themes", generate_table_grid)
    write_pages(themes_remixed, "remixed", "Remixed Themes", generate_table_grid)
    
    write_pages(themes_icon_packs, "icons_themes", "Theme Icon Packs", generate_icon_pack_table)
    write_pages(standalone_icon_packs, "icons_standalone", "Standalone Icon Packs", generate_icon_pack_table)

    write_file(from_src("../README.md"), generate_index({
        "custom": len(themes_custom),
        "remixed": len(themes_remixed),
        "icons_themes": len(themes_icon_packs),
        "icons_standalone": len(standalone_icon_packs)
    }))

    print("Done")


def write_file(path: str, buffer: str):
    with open(path, "w+", encoding="utf-8") as outfile:
        outfile.write(buffer)


def apply_template(path: str, data: dict) -> str:
    with open(path, "r", encoding="utf-8") as file:
        template = Template(file.read())
    return template.substitute(data) + "\n"


def format_page_filename(page: int) -> str:
    return "README.md" if page == 0 else f"README.p{page+1:02}.md"


def generate_index(counts: dict):
    buffer = ""
    buffer += apply_template(HEADER_TEMPLATE, { "LINKS": generate_header_links(".") })
    buffer += """## Welcome to the Onion Theme Repository!

*Click on a section below to browse themes and icon packs*
    
"""
    
    for group_name, count in counts.items():
        text, link = HEADER_LINKS[group_name]
        buffer += f"""
### [{text} ({count})]({rel_path(link, ".")})

"""

    buffer += "<p>&nbsp;</p>\n\n---\n\n<p>&nbsp;</p>\n\n> *We've dialed down the front page, to lower the amount of consecutive image loads - this was causing severe throttling issues for non-users*"
    return buffer


def write_pages(items: list, group_name: str, group_header: str, item_grid_generator: Callable[[list], str], page_size: int = 12, **opts):
    workdir = os.path.join(PAGES_DIR, group_name)
    os.makedirs(workdir, exist_ok=True)

    total = len(items)
    num_pages = math.ceil(total / page_size)

    for page in tqdm(range(num_pages), desc=group_header):
        current_path = os.path.join(workdir, format_page_filename(page))

        index = page * page_size
        batch = items[index  : index + page_size]
        last_item = min(index + page_size, total)
        
        buffer = ""
        buffer += apply_template(HEADER_TEMPLATE, { "LINKS": generate_header_links(current_path, current_group=group_name) })
        buffer += f"""
## {group_header}

**Page {page + 1} of {num_pages}**  
*Showing {index + 1}–{last_item} of {total} items*
"""
        buffer += item_grid_generator(batch, **opts) + "\n\n"

        if num_pages > 1:
            buffer += generate_pagination(page, num_pages)

        write_file(current_path, buffer)


def generate_header_links(current_path: str, current_group: str = None):
    links = []
    for group_name, [ text, link ] in HEADER_LINKS.items():
        if group_name == current_group:
            links.append(f"**{text}**")
        else:
            links.append(f"[{text}]({rel_path(link, current_path)})")
    return " &nbsp;•&nbsp; ".join(links)


def generate_pagination(current_page: int, num_pages: int) -> str:
    buffer = ""

    buffer += """---\n\n<table align="center"><tr><td align="center" valign="top">\n\n"""

    if current_page > 0:
        buffer += f"[🡄&nbsp;PREV&nbsp;PAGE]({format_page_filename(current_page - 1)})&nbsp;&nbsp;|&nbsp;&nbsp;"

    for page in range(num_pages):        
        if page == current_page:
            buffer += f"**{page + 1:02}**"
        else:
            buffer += f"[{page + 1:02}]({format_page_filename(page)})"
        if page < num_pages - 1:
            buffer += "&nbsp;&nbsp;"

    if current_page < num_pages - 1:
        buffer += f"&nbsp;&nbsp;|&nbsp;&nbsp;[NEXT&nbsp;PAGE&nbsp;🡆]({format_page_filename(current_page + 1)})"

    buffer += """</td></tr></table>"""

    return buffer


def generate_table_grid(themes, cols: int = THEMES_COLS) -> str:
    buffer = ""

    for i, theme in enumerate(themes):
        if i > 0 and i % cols == 0:
            buffer += "</tr><tr>\n"
        buffer += generate_item(theme)

    return apply_template(GRID_TEMPLATE, {"GRID_ITEMS": buffer})


def generate_item(theme: str) -> str:
    dir_path = os.path.join(THEME_DIR, theme)
    is_valid, has_subdirs = validate_theme(dir_path)

    if not is_valid:
        print(f"  invalid theme: {theme}")
        return ""

    title = ""
    name_split = theme.split(" by ", maxsplit=1)
    name = name_split[0]
    author = name_split[1] if len(name_split) > 1 else ""

    is_featured = theme in themes_featured

    if not has_subdirs:
        with open(os.path.join(dir_path, "config.json"), "r", encoding="utf-8") as infile:
            config = json.load(infile)
        if "name" in config:
            name = config["name"]
        if "author" in config:
            author = config["author"]
        if "description" in config:
            title = config["description"]

    if not title:
        title = f"{name} by {author}" if author else name
    if is_featured:
        title += " [featured theme]"

    theme_subdirs = [f"themes/{theme}/{subdir}" for subdir in get_subdirs(dir_path)] if has_subdirs else [f"themes/{theme}"]

    if os.path.exists(f"themes/{theme}/preview.png"):
        preview_url = f"https://raw.githubusercontent.com/OnionUI/Themes/main/themes/{urlencode(theme)}/preview.png"
    else:
        preview_url = f"https://raw.githubusercontent.com/OnionUI/Themes/main/{urlencode(theme_subdirs[0])}/preview.png"
    release_url = f"https://raw.githubusercontent.com/OnionUI/Themes/main/release/{urlencode(theme)}.zip"
    history_url = f"https://github.com/OnionUI/Themes/commits/main/themes/{theme}"

    last_updated = git_last_changed(dir_path)
    last_updated = last_updated.strftime("%Y-%m-%d") if last_updated is not None else ""

    bgm_path = from_src(f"../{theme_subdirs[0]}/sound/bgm.mp3")
    has_bgm = os.path.isfile(bgm_path)

    has_icon_pack = any(os.path.isdir(f"{subdir}/icons") for subdir in theme_subdirs)
    
    readme_path = ""

    for readme_file in README_TEST:
        for subdir in theme_subdirs:
            readme_path = os.path.join(subdir, readme_file)
            if os.path.isfile(readme_path):
                break
            readme_path = ""
        if readme_path != "":
            break

    item = {
        "NAME": name + " ★" if is_featured else name,
        "AUTHOR": author or "&nbsp;",
        "TITLE": title,
        "HAS_BGM": f"&nbsp;&nbsp;<a href=\"https://onionui.github.io/bgm_preview.html?theme={urlencode(theme_subdirs[0][7:])}\">{BGM_ICON}</a>" if has_bgm else "",
        "HAS_ICONPACK": f"&nbsp; <a href=\"{generate_icon_pack_url(theme, theme_subdirs)}\">{HAS_ICONPACK_ICON}</a>" if has_icon_pack else "",
        "README": f"&nbsp;&nbsp;<a href=\"{urlencode(readme_path)}\">{README_ICON}</a>" if len(readme_path) != 0 else "",
        "AUTHOR_BTN": f"&nbsp;&nbsp;<a href=\"https://github.com/search?l=ZIP&q=filename%3A%22{urlencode(author)}%22+repo%3AOnionUI%2FThemes\">{AUTHOR_ICON}</a>" if author else "",
        "UPDATED": last_updated,
        "PREVIEW_URL": preview_url,
        "RELEASE_URL": release_url,
        "HISTORY_URL": history_url
    }

    if has_icon_pack:
        for subdir in theme_subdirs:
            if os.path.isdir(f"{subdir}/icons") and os.path.basename(subdir) not in icons_blacklist:
                themes_icon_packs.append({
                    "name": os.path.basename(subdir),
                    "path": from_src(os.path.join("..", subdir, "icons")),
                    "is_theme": True,
                    "theme": theme,
                    "release_url": release_url,
                    "preview_url": generate_icon_pack_url(theme, [subdir])
                })

    return apply_template(ITEM_TEMPLATE, item)


def generate_icon_pack_url(theme: str, theme_subdirs: list[str]) -> str:
    icons_dirs = [f"{subdir}/icons" for subdir in theme_subdirs if os.path.isdir(f"{subdir}/icons") and os.path.basename(subdir) not in icons_blacklist]

    url = f"https://onionui.github.io/iconpack_preview.html#{urlencode(theme)},"
    url += ",".join(f"{urlencode(os.path.basename(os.path.dirname(icons_dir)))}:{urlencode(icons_dir)}" for icons_dir in icons_dirs)

    return url


if __name__ == "__main__":
    main()
