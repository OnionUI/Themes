import os
import math
from PIL import Image

from defs import *
from utils import get_lines, urlencode


PREVIEW_ICONS = ["fc", "gb", "gba", "gbc", "md", "ms", "ps", "sfc"]
ALL_ICONS = ['32X', '5200', '7800', 'amiga', 'arcade', 'atari', 'c64', 'col', 'cpc', 'cps1', 'cps2', 'cps3', 'dos', 'fairchild', 'fc', 'fds', 'gb', 'gba', 'gbc', 'gg', 'gw', 'itv', 'lynx', 'md', 'megaduck', 'ms', 'msx', 'nds', 'neocd', 'neogeo', 'ngp', 'ody', 'pce', 'pcecd', 'pico', 'poke', 'ports', 'ps', 'satella', 'scummvm', 'search', 'segacd', 'segasgone', 'sfc', 'sgb', 'sgfx', 'sufami', 'supervision', 'tic', 'vb', 'vdp', 'vectrex', 'ws', 'zxs']


def get_ordered_icons() -> list[dict]:
    ordered_icons = []
    icon_packs = []

    for dir_name in os.listdir("icons"):
        dir_path = os.path.join("icons", dir_name)
        release_url = os.path.join("release", dir_path + ".zip")

        if not os.path.isfile(release_url):
            continue

        icon_packs.append({
            "name": dir_name,
            "path": from_src(os.path.join("..", dir_path)),
            "release_url": f"https://raw.githubusercontent.com/OnionUI/Themes/main/{urlencode(release_url)}",
            "preview_url": f"https://onionui.github.io/iconpack_preview.html#{urlencode(dir_name)}"
        })

    for icon_pack in get_lines(ICONS_ORDERING):
        result = next((x for x in icon_packs if x['name'] == icon_pack), None)
        if result is None:
            continue
        ordered_icons.append(result)

    ordered_icons.reverse()

    return ordered_icons


def generate_icon_pack_table(icon_packs: list[dict], cols: int = ICONS_COLS) -> str:
    current_path = os.path.join(PAGES_ICONS_DIR, ".")
    output = "<table align=center><tr>\n\n"
    
    for i, icon_pack in enumerate(icon_packs):
        if i > 0 and i % cols == 0:
            output += "</tr><tr>\n"
        output += generate_icon_pack_entry(current_path, **icon_pack, index=i)

    output += "</tr></table>\n\n"

    return output


def generate_icon_pack_entry(current_path: str, name, path, release_url, preview_url, is_theme: bool = False, theme: str = "", index: int = 0):
    preview_path = from_src(os.path.join(path, f"preview.png"))

    ensure_has_icon_preview(path)

    output = f"""
<td valign="top">

#### {name}

![{name}]({urlencode(rel_path(preview_path, current_path))})

"""

    if len(release_url) != 0:
        dn_text = f"Download {theme} (theme)" if is_theme else f"Download {name} (icon pack)"
        output += f"[{dn_text}]({release_url})\n\n"

    readme_path = ""

    for readme_file in README_TEST + [f"../{fn}" for fn in README_TEST]:
        readme_path = os.path.abspath(from_src(os.path.join("..", path, readme_file)))
        if os.path.isfile(readme_path):
            readme_path = readme_path[len(REL_PATH):]
            break
        readme_path = ""

    readme = f"<a href=\"{urlencode(readme_path)}\">{README_ICON}</a> &nbsp;&nbsp; " if len(readme_path) != 0 else ""

    icon_count = sum(os.path.isfile(f"{path}/{icon}.png") for icon in ALL_ICONS)
    output += f"<sub><sup>{icon_count}/{len(ALL_ICONS)} icons ({round(icon_count/len(ALL_ICONS)*100)}% complete)</sup> &nbsp;&nbsp; {readme}<a href=\"{preview_url}\">{PREVIEW_ICON}</a></sub>"

    output += f"\n\n{ICONS_COLUMN_SPANNER if index < ICONS_COLS else ''}<br/></td>\n\n"

    return output


def generate_preview_image(output_path: str, icon_paths: list[str], cols: int = 2, rows: int = 4, w: int = 250, h: int = 360):
    images = [Image.open(path) for path in icon_paths]

    output = Image.new("RGBA", (w, h))
    icon_w = math.floor(w / cols)
    icon_h = math.floor(h / rows)

    for index, image in enumerate(images):
        x = math.floor(index % cols)
        y = math.floor(index / cols)
        image.thumbnail((icon_w, icon_h), Image.BICUBIC)
        pos_x = x * icon_w + math.floor((icon_w - image.width) / 2)
        pos_y = y * icon_h + math.floor((icon_h - image.height) / 2)
        output.paste(image, (pos_x, pos_y))

    output.save(output_path)


def ensure_has_icon_preview(icons_dir: str):
    if not os.path.isdir(icons_dir):
        return

    preview_path = os.path.join(icons_dir, f"preview.png")

    if not os.path.isfile(preview_path):
        print(f"Generating icon pack preview: {preview_path}")
        icon_paths = [os.path.join(icons_dir, f"{icon}.png") for icon in PREVIEW_ICONS]
        icon_paths_exist = [p for p in icon_paths if os.path.isfile(p)]

        if len(icon_paths_exist) == 0:
            return
        
        generate_preview_image(preview_path, icon_paths_exist)
