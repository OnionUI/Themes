import os
from collections import defaultdict
from defs import from_src

PRINT_NAMES = False


def main():
    dir_path = from_src("../release")

    counts = defaultdict(lambda: 0)
    themes = defaultdict(lambda: [])

    for path in os.listdir(dir_path):
        if not os.path.isfile(os.path.join(dir_path, path)):
            continue

        if " by " not in path:
            continue

        theme_name, authors = os.path.splitext(path)[0].split(" by ")
        authors = authors.split(" + ")

        for author in authors:
            counts[author] += 1
            themes[author].append(theme_name)

    for author, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{author} ({count})")

        if PRINT_NAMES:
            print(f"({', '.join(sorted(themes[author]))})")


if __name__ == "__main__":
    main()
