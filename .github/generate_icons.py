import os
import math
from PIL import Image

from defs import *
from utils import get_lines, urlencode


PREVIEW_ICONS = ["fc", "gb", "gba", "gbc", "md", "ms", "ps", "sfc"]
ALL_ICONS = ['32X', '5200', '7800', 'amiga', 'arcade', 'atari', 'c64', 'col', 'cpc', 'cps1', 'cps2', 'cps3', 'dos', 'fairchild', 'fc', 'fds', 'gb', 'gba', 'gbc', 'gg', 'gw', 'itv', 'lynx', 'md', 'megaduck', 'ms', 'msx', 'nds', 'neocd', 'neogeo', 'ngp', 'ody', 'pce', 'pcecd', 'pico', 'poke', 'ports', 'ps', 'satella', 'scummvm', 'search', 'segacd', 'segasgone', 'sfc', 'sgb', 'sgfx', 'sufami', 'supervision', 'tic', 'vb', 'vdp', 'vectrex', 'ws', 'zxs']


icons_blacklist = get_lines(ICONS_BLACKLIST)


class IconPack:
    def __init__(self, dir_name: str, dir_path: str, release_url: str = None, theme: str = None, theme_subdir: str = None):
        self.name = dir_name
        self.path = from_src(os.path.join("..", dir_path))
        self.release_url = f"https://raw.githubusercontent.com/OnionUI/Themes/main/{urlencode(os.path.join("release", dir_path + ".zip"))}" \
            if not release_url else release_url
        self.preview_url = generate_icon_pack_url(dir_name, theme_subdirs=[theme_subdir] if theme_subdir else None)
        self.is_theme = theme is not None
        self.theme = theme


def generate_icon_pack_url(dir_name: str, theme_subdirs: list[str] = None) -> str:
    url = f"https://onionui.github.io/iconpack_preview.html#{urlencode(dir_name)}"
    if theme_subdirs:
        icons_dirs = [f"{subdir}/icons" for subdir in theme_subdirs if os.path.isdir(f"{subdir}/icons") and os.path.basename(subdir) not in icons_blacklist]
        url += "," + ",".join(f"{urlencode(os.path.basename(os.path.dirname(icons_dir)))}:{urlencode(icons_dir)}" for icons_dir in icons_dirs)
    return url


def get_ordered_icons() -> list[dict]:
    ordered_icons: list[IconPack] = []
    icon_packs: list[IconPack] = []

    for dir_name in os.listdir("icons"):
        dir_path = os.path.join("icons", dir_name)
        if not os.path.isfile(os.path.join("release", dir_path + ".zip")):
            continue
        icon_packs.append(IconPack(dir_name, dir_path))

    for icon_pack in get_lines(ICONS_ORDERING):
        result = next((x for x in icon_packs if x.name == icon_pack), None)
        if result:
            ordered_icons.append(result)

    ordered_icons.reverse()

    return ordered_icons


def generate_icon_pack_table(icon_packs: list[IconPack]) -> str:
    current_path = os.path.join(PAGES_ICONS_DIR, ".")
    buffer = "<table align=center><tr>\n\n"
    
    for i, icon_pack in enumerate(icon_packs):
        if i > 0 and i % ICONS_COLS == 0:
            buffer += "</tr><tr>\n"
        buffer += generate_icon_pack_entry(current_path, icon_pack, index=i)

    buffer += "</tr></table>\n\n"

    return buffer


def generate_icon_pack_entry(current_path: str, icon_pack: IconPack, index: int = 0):
    preview_path = from_src(os.path.join(icon_pack.path, f"preview.png"))

    ensure_has_icon_preview(icon_pack.path)

    buffer = f"""\n<td valign="top" width="{100 / ICONS_COLS:.2f}%">\n\n"""
    buffer += f"""[![{icon_pack.name}]({urlencode(rel_path(preview_path, current_path))})]({icon_pack.preview_url} "Click to see the full icon pack preview page")\n\n"""
    buffer += f"**{icon_pack.name}**\n\n"

    dn_text = f"Download theme" if icon_pack.is_theme else f"Download icon pack"
    dn_link = f"[{dn_text}]({icon_pack.release_url} \"{icon_pack.theme if icon_pack.is_theme else icon_pack.name}\")"

    readme_path = ""

    for readme_file in README_TEST + [f"../{fn}" for fn in README_TEST]:
        readme_path = os.path.abspath(from_src(os.path.join("..", icon_pack.path, readme_file)))
        if os.path.isfile(readme_path):
            readme_path = readme_path[len(REL_PATH):]
            break
        readme_path = ""

    readme = f"<a href=\"{urlencode(readme_path)}\">{README_ICON}</a> {NB_SPACER} " if len(readme_path) != 0 else ""

    icon_count = sum(os.path.isfile(f"{icon_pack.path}/{icon}.png") for icon in ALL_ICONS)
    buffer += f"{dn_link} <sub><sup>{NB_SPACER} {icon_count / len(ALL_ICONS) * 100:.0f}%{NB_SPACE}complete</sup> {NB_SPACER} {readme}</sub>"

    buffer += f"\n\n{ICONS_COLUMN_SPANNER if index < ICONS_COLS else ''}<br/></td>\n\n"

    return buffer


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


def ensure_has_icon_preview(icons_dir: str, force_mode: bool = False):
    if not os.path.isdir(icons_dir):
        return

    preview_path = os.path.join(icons_dir, f"preview.png")

    if not os.path.isfile(preview_path) or force_mode:
        icon_paths = [find_icon(icons_dir, icon, try_selected=i == 2) for i, icon in enumerate(PREVIEW_ICONS)]
        icon_paths_exist = [p for p in icon_paths if p]

        if len(icon_paths_exist) == 0:
            return
        
        print(f"Generating icon pack preview: {preview_path}")
        generate_preview_image(preview_path, icon_paths_exist)


def find_icon(icons_dir: str, icon: str, try_selected: bool):
    if try_selected:
        path = os.path.join(icons_dir, "sel", f"{icon}.png")
        if os.path.isfile(path):
            return path
    path = os.path.join(icons_dir, f"{icon}.png")
    return path if os.path.isfile(path) else None
