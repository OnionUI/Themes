#!/usr/bin/python3

import os
import sys
import zipfile

from defs import (
    THEME_DIR,
    RELEASE_DIR,
    FEATURED_ORDERING,
    REMIXED_ORDERING,
    CUSTOM_ORDERING)

from utils import get_subdirs, get_ordering, set_ordering
from validation import validate_theme
from generate import main as generate_readme
from clean import clean_all


def main():
    yes_to_all = "-y" in sys.argv
    no_to_all = "-n" in sys.argv

    if not os.path.exists(THEME_DIR):
        print("No themes to build")
        return

    themes = get_subdirs(THEME_DIR)

    if not os.path.exists(RELEASE_DIR):
        os.makedirs(RELEASE_DIR)

    featured = get_ordering(FEATURED_ORDERING)
    remixed = get_ordering(REMIXED_ORDERING)
    custom = get_ordering(CUSTOM_ORDERING)
    all_existing = featured + remixed + custom

    clean_all()

    was_built = [build_release(theme, custom, all_existing) for theme in themes]

    set_ordering(CUSTOM_ORDERING, custom)

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

    if os.path.exists(zip_path):
        return False

    print(f"Building release: '{theme}'")

    is_valid, has_subdirs = validate_theme(src_path)

    if not is_valid:
        print(f"Skipped: '{theme}'")
        return False

    if theme not in all_existing:
        custom.append(theme)

    rel_index = len(src_path if has_subdirs else os.path.dirname(src_path)) + 1

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(src_path):
            if os.path.basename(root) == ".trash":
                continue
            for file in files:
                if has_subdirs and root == src_path and file == "preview.png":
                    continue
                file_path = os.path.join(root, file)
                zf.write(file_path, file_path[rel_index:])

    return True


if __name__ == "__main__":
    main()
