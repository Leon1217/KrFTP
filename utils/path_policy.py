from __future__ import annotations

from pathlib import Path


def resolve_under_root(root_path: str, requested_path: str) -> Path:
    root = Path(root_path).resolve()
    requested = Path(requested_path)
    target = requested.resolve() if requested.is_absolute() else (root / requested_path.lstrip("/\\")).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise PermissionError("Path escapes the authorized root") from exc
    return target
