from __future__ import annotations

import zipfile
from pathlib import Path

from .path_policy import resolve_under_root

MAX_ARCHIVE_FILES = 10_000
MAX_EXTRACTED_BYTES = 2 * 1024 * 1024 * 1024


def create_zip(root_path: str, source_path: str, archive_path: str) -> Path:
    source = resolve_under_root(root_path, source_path)
    archive = resolve_under_root(root_path, archive_path)
    if not source.exists():
        raise FileNotFoundError(source)
    archive.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as output:
        if source.is_dir():
            for item in source.rglob("*"):
                if item.is_file() and item.resolve() != archive:
                    output.write(item, item.relative_to(source.parent))
        else:
            output.write(source, source.name)
    return archive


def extract_zip(root_path: str, archive_path: str, destination: str) -> Path:
    archive = resolve_under_root(root_path, archive_path)
    output = resolve_under_root(root_path, destination)
    with zipfile.ZipFile(archive) as source:
        infos = source.infolist()
        if len(infos) > MAX_ARCHIVE_FILES or sum(item.file_size for item in infos) > MAX_EXTRACTED_BYTES:
            raise ValueError("Archive exceeds extraction limits")
        for info in infos:
            target = resolve_under_root(str(output), info.filename)
            if target != output and not str(target).startswith(str(output)):
                raise PermissionError("Unsafe archive entry")
        source.extractall(output)
    return output
