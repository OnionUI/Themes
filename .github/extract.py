#!/usr/bin/python3

import os
import sys
import shutil
import zipfile

from defs import (
    THEME_DIR,
    RELEASE_DIR,
    TEMP_DIR)

from utils import get_files, get_subdirs
from validation import validate_theme
from clean import clean_all


def main():
    if not os.path.exists(RELEASE_DIR):
        print("No themes to extract")
        return

    theme_zips = get_files(RELEASE_DIR)

    if not os.path.exists(THEME_DIR):
        os.makedirs(THEME_DIR)

    was_extracted = [
        extract_release(os.path.join(RELEASE_DIR, zip_file))
        for zip_file in theme_zips]

    if any(was_extracted):
        clean_all()
    else:
        print("Nothing to do.")


def extract_release(zip_path: str):
    theme, _ = os.path.splitext(os.path.basename(zip_path))
    src_path = os.path.join(THEME_DIR, theme)

    if os.path.exists(src_path):
        return False

    print(f"Extracting release: '{theme}'")

    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)

    with zipfile.ZipFile(zip_path, "r", zipfile.ZIP_DEFLATED) as zf:
        zf.extractall(TEMP_DIR)

    is_valid, has_subdirs = validate_theme(TEMP_DIR, True)

    if not is_valid:
        return False

    if has_subdirs:
        subdirs = get_subdirs(TEMP_DIR)
        root = THEME_DIR if len(subdirs) == 1 else src_path
        for subdir in subdirs:
            dir_path = os.path.join(TEMP_DIR, subdir)
            shutil.move(dir_path, os.path.join(root, subdir))
    else:
        shutil.move(TEMP_DIR, src_path)

    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)

    os.remove(zip_path)

    return True


if __name__ == "__main__":
    main()
