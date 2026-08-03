#!/usr/bin/env python3
"""Validate the portable subset of the Agent Skills specification."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict


ALLOWED_KEYS = {"name", "description"}
NAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")


def parse_frontmatter(path: Path) -> Dict[str, str]:
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("SKILL.md 必须以 YAML frontmatter 开始")

    try:
        end = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration as exc:
        raise ValueError("SKILL.md 缺少 frontmatter 结束标记") from exc

    data: Dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[:1].isspace() or ":" not in line:
            raise ValueError(f"不支持的 frontmatter 行：{line}")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key in data:
            raise ValueError(f"重复字段：{key}")
        data[key] = value.strip('"\'')
    return data


def validate_skill(skill_dir: Path, expected_name: str = "", require_folder_match: bool = False) -> None:
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        raise ValueError(f"缺少文件：{skill_file}")
    data = parse_frontmatter(skill_file)

    unexpected = set(data) - ALLOWED_KEYS
    if unexpected:
        raise ValueError(f"不兼容的 frontmatter 字段：{', '.join(sorted(unexpected))}")
    if set(data) != ALLOWED_KEYS:
        raise ValueError("frontmatter 必须且只能包含 name 和 description")

    name = data["name"]
    description = data["description"]
    if not NAME_RE.fullmatch(name):
        raise ValueError("name 必须为 1-64 位小写字母、数字或连字符")
    if expected_name and name != expected_name:
        raise ValueError(f"name 应为 {expected_name}，实际为 {name}")
    if require_folder_match and name != skill_dir.resolve().name:
        raise ValueError(f"name {name} 与目录名 {skill_dir.resolve().name} 不一致")
    if not description or len(description) > 1024:
        raise ValueError("description 必须为 1-1024 个字符")


def main() -> None:
    parser = argparse.ArgumentParser(description="校验 Agent Skill")
    parser.add_argument("skill_dir", type=Path)
    parser.add_argument("--expected-name", default="")
    parser.add_argument("--require-folder-match", action="store_true")
    args = parser.parse_args()
    try:
        validate_skill(args.skill_dir, args.expected_name, args.require_folder_match)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
    print(f"OK: {args.skill_dir / 'SKILL.md'}")


if __name__ == "__main__":
    main()
