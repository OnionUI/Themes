import os
from urllib.parse import quote as _quote
import subprocess
from datetime import datetime


urlencode = lambda s: _quote(s, safe="/?&=_-")


def get_subdirs(dir_path: str):
    subdirs = [
        name for name in os.listdir(dir_path)
        if os.path.isdir(os.path.join(dir_path, name)) and name != "__MACOSX"]
    subdirs.sort()
    return subdirs


def get_files(dir_path: str, ext: str = None):
    files = [
        name for name in os.listdir(dir_path)
        if os.path.isfile(os.path.join(dir_path, name)) and
        (ext is None or has_extension(name, ext))]
    files.sort()
    return files


def has_extension(name: str, required_ext: str) -> bool:
    _, ext = os.path.splitext(name)
    return ext[1:].lower() == required_ext


def get_ordering(file_path: str) -> list[str]:
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as file:
        lines = [line.rstrip() for line in file.readlines()]
    return lines


def set_ordering(file_path: str, ordering: list[str]):
    with open(file_path, "w+", encoding="utf-8") as file:
        for line in ordering:
            file.write(line + "\n")


def dir_has_files(dir_path: str, files: list[str]):
    return all(os.path.exists(os.path.join(dir_path, file)) for file in files)


def git_last_changed(path: str) -> datetime:
    git_result = subprocess.run(["git", "log", "-1", "--pretty=%cI", path], stdout=subprocess.PIPE, check=True)
    datestr = git_result.stdout.decode('utf-8').strip()
    if 'T' in datestr:
        datestr = datestr.split("T")[0]
    return datetime.fromisoformat(datestr).strftime("%Y-%m-%d") if datestr else None
