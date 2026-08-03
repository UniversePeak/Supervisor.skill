"""Shared path validation and atomic-write helpers."""

from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path


SLUG_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
VERSION_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9._-]{0,126}[A-Za-z0-9])?$")


def validate_slug(value: str) -> str:
    if not SLUG_RE.fullmatch(value or ""):
        raise ValueError("slug 必须为 1-64 位小写字母、数字或连字符，且不能以连字符开头或结尾")
    return value


def validate_version(value: str) -> str:
    if not VERSION_RE.fullmatch(value or ""):
        raise ValueError("版本名只能包含字母、数字、点、下划线和连字符")
    return value


def ensure_within(base_dir: Path, candidate: Path) -> Path:
    base = base_dir.expanduser().resolve()
    resolved = candidate.expanduser().resolve()
    try:
        resolved.relative_to(base)
    except ValueError as exc:
        raise ValueError(f"路径超出允许目录：{resolved}") from exc
    return resolved


def safe_child(base_dir: Path, segment: str, *, kind: str = "slug") -> Path:
    if kind == "slug":
        validate_slug(segment)
    elif kind == "version":
        validate_version(segment)
    else:
        raise ValueError(f"未知路径片段类型：{kind}")
    return ensure_within(base_dir, base_dir.expanduser() / segment)


def atomic_write_text(path: Path, content: str, *, encoding: str = "utf-8") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding=encoding,
            dir=str(path.parent),
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temp_name = handle.name
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if temp_name and os.path.exists(temp_name):
            os.unlink(temp_name)
