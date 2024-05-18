#!/usr/bin/python3

import os
import sys
import zipfile

from defs import *

from utils import get_subdirs, get_lines, set_ordering, git_last_changed
from validation import validate_theme
from generate import main as generate_readme
from clean import clean_all, clean_unwanted_files
from generate_icons import ensure_has_icon_preview


def main():
    yes_to_all = "-y" in sys.argv
    no_to_all = "-n" in sys.argv

    if not os.path.exists(THEME_DIR):
        print("No themes to build")
        return

    themes = get_subdirs(THEME_DIR)

    if not os.path.exists(RELEASE_ICONS_DIR):
        os.makedirs(RELEASE_ICONS_DIR)

    featured = get_lines(FEATURED_ORDERING)
    remixed = get_lines(REMIXED_ORDERING)
    custom = get_lines(CUSTOM_ORDERING)
    all_existing = featured + remixed + custom

    all_icons = get_lines(ICONS_ORDERING)

    clean_all()

    was_built = [build_release(theme, custom, all_existing) for theme in themes] + [build_icon_pack(icon_pack, all_icons) for icon_pack in os.listdir("icons")]

    set_ordering(CUSTOM_ORDERING, custom)
    set_ordering(ICONS_ORDERING, all_icons)

    if any(was_built):
        if no_to_all:
            return
        if yes_to_all or input("Generate README? [Y/n] ").lower() in ["y", ""]:
            generate_readme()
    else:
        print("Nothing to do.")


def build_release(theme: str, custom: list[str], all_existing: list[str]):
    src_path = os.path.join(THEME_DIR, theme)
    zip_path = os.path.join(RELEASE_DIR, f"{theme}.zip")

    if should_skip_build(src_path, zip_path):
        return False

    print(f"Building release: '{theme}'")

    is_valid, has_subdirs = validate_theme(src_path)

    if not is_valid:
        print(f"Skipped: '{theme}'")
        return False

    if theme not in all_existing:
        custom.append(theme)
        
    ensure_has_icon_preview(os.path.join(src_path, "icons"), force_mode=True)

    rel_index = len(src_path if has_subdirs else os.path.dirname(src_path)) + 1

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(src_path):
            if os.path.basename(root) == ".trash":
                continue
            for file in files:
                if has_subdirs and root == src_path and file == "preview.png":
                    continue
                if file == "md5hash":
                    continue
                file_path = os.path.join(root, file)
                zf.write(file_path, file_path[rel_index:])

    return True


def build_icon_pack(icon_pack, all_icons) -> bool:
    src_path = os.path.join("icons", icon_pack)
    zip_path = os.path.join(RELEASE_ICONS_DIR, f"{icon_pack}.zip")

    if icon_pack not in all_icons:
        all_icons.append(icon_pack)

    if should_skip_build(src_path, zip_path):
        return False

    clean_unwanted_files(src_path)
    ensure_has_icon_preview(src_path, force_mode=True)

    rel_index = len(os.path.dirname(src_path)) + 1

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(src_path):
            for file in files:
                file_path = os.path.join(root, file)
                zf.write(file_path, file_path[rel_index:])

    return True


def should_skip_build(src_path: str, zip_path: str) -> bool:
    if not os.path.exists(zip_path):
        return False
    
    src_last_changed = git_last_changed(src_path)

    if not src_last_changed:
        return False

    zip_last_changed = git_last_changed(zip_path)

    if not zip_last_changed or src_last_changed.date() > zip_last_changed.date():
        return False
    
    return True


if __name__ == "__main__":
    main()
