#!/usr/bin/python3

import os
import shutil

from defs import THEME_DIR


UNNECESSARY_FILES = ["Thumbs.db", ".DS_Store"]


def clean_all():
    for root, _, files in os.walk(THEME_DIR):
        if os.path.basename(root) == "__MACOSX":
            shutil.rmtree(root)
            continue
        for file in files:
            _, ext = os.path.splitext(file)
            file_path = os.path.join(root, file)
            if file.startswith("._") or file in UNNECESSARY_FILES or ext.lower() == ".html":
                os.remove(file_path)


if __name__ == "__main__":
    clean_all()
