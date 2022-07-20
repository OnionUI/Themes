import os
import sys

from defs import THEME_DIR
from utils import dir_has_files, get_subdirs


def main():
    if not os.path.exists(THEME_DIR):
        print("No themes to validate")
        return

    themes = get_subdirs(THEME_DIR)

    is_valid = [validate_theme(os.path.join(THEME_DIR, theme), theme, True)[0] for theme in themes]

    if not all(is_valid):
        sys.exit(1)

    print("All themes are valid.")


def validate_theme(src_path: str, theme: str, verbose: bool = False, level: int = 0):
    has_config = dir_has_files(src_path, ["config.json"])

    # Check subdirs
    if not has_config:
        if level == 0:
            return (all(validate_theme(os.path.join(src_path, subdir), subdir, True, level + 1)[0]
                        for subdir in get_subdirs(src_path)), True)
        return (False, False)

    if verbose and not has_config:
        print(f"Theme '{theme}' is missing config.json")

    has_preview = dir_has_files(src_path, ["preview.png"])

    is_valid = has_config and has_preview

    return (is_valid, False)


if __name__ == "__main__":
    main()
