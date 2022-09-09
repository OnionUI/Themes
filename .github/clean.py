#!/usr/bin/python3

import os
import sys
import shutil
import json
from numbers import Number

from defs import THEME_DIR, from_src
from schema import config_schema

UNWANTED_FOLDERS = ["__MACOSX", "skin_640_480"]
UNWANTED_FILES = ["Thumbs.db", ".DS_Store"]

args_theme_dir = THEME_DIR
args_allow_system = False


def clean_all():
    clean_unwanted_files(args_theme_dir)
    clean_unused_images(args_theme_dir, args_allow_system)
    clean_configs(args_theme_dir)


def clean_unwanted_files(theme_dir):
    dir_count = 0
    file_count = 0
    for root, _, files in os.walk(theme_dir):
        if os.path.basename(root) in UNWANTED_FOLDERS:
            dir_count += 1
            shutil.rmtree(root)
            continue
        for file in files:
            _, ext = os.path.splitext(file)
            file_path = os.path.join(root, file)
            if file.startswith("._") or file in UNWANTED_FILES or ext.lower() == ".html":
                file_count += 1
                os.remove(file_path)
    if (dir_count + file_count) == 0:
        print("OK - No unwanted files found (Mac dotfiles, etc)")
    else:
        print(f"WARN - Removed {file_count} unwanted files and {dir_count} folders")


def clean_unused_images(theme_dir, allow_system: bool = False):
    with open(from_src("whitelist.txt"), "r", encoding="utf-8") as fp:
        lines = fp.readlines()

    if allow_system:
        with open(from_src("whitelist_system.txt"), "r", encoding="utf-8") as fp:
            lines += fp.readlines()

    whitelist = [line.strip() for line in lines]

    with open(from_src("whitelist_extra.txt"), "r", encoding="utf-8") as fp:
        lines = fp.readlines()
    whitelist_extra = [line.strip() for line in lines]

    extra_count = 0
    trash_count = 0

    for root, _, files in os.walk(theme_dir):
        if os.path.basename(root) != "skin":
            continue

        theme = os.path.basename(os.path.dirname(root))
        trash_dir = os.path.join(root, ".trash")
        extra_dir = os.path.join(root, "extra")

        for file in files:
            name, ext = os.path.splitext(file)
            if ext.lower() != ".png":
                continue
            file_path = os.path.join(root, file)

            if name == "power-full-icon_back":
                restore_path = os.path.join(root, "power-full-icon.png")
                if not os.path.exists(trash_dir):
                    os.makedirs(trash_dir)
                trash_count += 1
                shutil.move(restore_path, trash_dir)
                os.rename(file_path, restore_path)
                print(f"restored: 'power-full-icon' ({theme})")

            if name not in whitelist:
                if name in whitelist_extra:
                    if not os.path.exists(extra_dir):
                        os.makedirs(extra_dir)
                    extra_count += 1
                    shutil.move(file_path, extra_dir)
                    print(f"extra: '{name}' ({theme})")
                    continue

                if not os.path.exists(trash_dir):
                    os.makedirs(trash_dir)
                trash_count += 1
                shutil.move(file_path, trash_dir)
                print(f"removed: '{name}' ({theme})")

    if (extra_count + trash_count) == 0:
        print("OK - No unused images found")
    else:
        print(f"WARN - Removed {trash_count} unused images, and moved {extra_count} to extra folder")


def clean_config(config: dict[str, any], schema = None) -> dict[str, any]:
    cleaned = {}
    dirty = False

    if schema is None:
        schema = config_schema

    if "hideLabels" not in config and "hideIconTitle" in config and config["hideIconTitle"]:
        config["hideLabels"] = { "icons": True, "hints": True }

    for key, value in config.items():
        if key not in schema:
            dirty = True
            continue
        if key == "name" and "author" not in config and (" by " in value or " - " in value):
            name, author = str(value).split(" by " if " by " in value else " - ", 1)[:2]
            cleaned["name"] = name
            cleaned["author"] = author
        elif isinstance(value, dict):
            cleaned[key], _dirty = clean_config(value, schema[key])
            if _dirty:
                dirty = True
        elif isinstance(value, schema[key]):
            cleaned[key] = value
        elif isinstance(value, Number) and isinstance(schema[key], int):
            cleaned[key] = round(value)
        else:
            dirty = True

    return (cleaned, dirty)


def clean_configs(theme_dir):
    rgb_to_hex = (lambda r, g, b:
        f"#{hex(r)[2:]}{hex(g)[2:]}{hex(b)[2:]}".upper())

    dirty_count = 0

    for root, _, _ in os.walk(theme_dir):
        if os.path.basename(root) != "skin":
            continue

        config_path = os.path.join(os.path.dirname(root), "config.json")

        if not os.path.exists(config_path):
            continue

        with open(config_path, "r", encoding="utf-8") as fp:
            config = json.load(fp)

        cleaned, dirty = clean_config(config)

        if "batteryPercentage" in config:
            bp = config["batteryPercentage"]
            if "color" not in bp and "red" in bp and "green" in bp and "blue" in bp:
                r, g, b = bp["red"], bp["green"], bp["blue"]
                dirty = True
                cleaned["batteryPercentage"]["color"] = rgb_to_hex(r, g, b)

        if dirty:
            dirty_count += 1

        with open(config_path, "w", encoding="utf-8") as fp:
            json.dump(cleaned, fp, indent=4)

    if dirty_count == 0:
        print("OK - All configs conformed to schema")
    else:
        print(f"WARN - Cleaned {dirty_count} configs")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        args_theme_dir = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[2] == "--system":
        args_allow_system = True
    clean_all()
