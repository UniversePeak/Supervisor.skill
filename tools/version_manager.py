#!/usr/bin/env python3
"""
导师 Skill 版本管理工具

支持：
1) list：列出历史版本
2) backup：备份当前版本
3) rollback：回滚到指定版本
4) cleanup：清理旧版本
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    from .path_safety import atomic_write_text, safe_child, validate_slug, validate_version
except ImportError:
    from path_safety import atomic_write_text, safe_child, validate_slug, validate_version


DEFAULT_MAX_KEEP = 15
CORE_FILES = ("SKILL.md", "method_core.md", "academic.md", "persona.md", "playbook.md", "meta.json")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_meta(skill_dir: Path) -> dict:
    meta_path = skill_dir / "meta.json"
    if not meta_path.exists():
        return {}
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_meta(skill_dir: Path, meta: dict) -> None:
    atomic_write_text(skill_dir / "meta.json", json.dumps(meta, ensure_ascii=False, indent=2))


def backup(skill_dir: Path, explicit_version: Optional[str] = None) -> Path:
    versions_dir = skill_dir / "versions"
    versions_dir.mkdir(parents=True, exist_ok=True)

    meta = load_meta(skill_dir)
    version = validate_version(explicit_version or meta.get("version", "v1"))
    target = safe_child(versions_dir, version, kind="version")
    if target.exists():
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        target = safe_child(versions_dir, f"{version}_{ts}", kind="version")
    target.mkdir(parents=True, exist_ok=True)

    copied = 0
    for name in CORE_FILES:
        src = skill_dir / name
        if src.exists():
            shutil.copy2(src, target / name)
            copied += 1
    print(f"OK: 备份完成 {target}（{copied} 个文件）")
    return target


def list_versions(skill_dir: Path) -> list[dict]:
    versions_dir = skill_dir / "versions"
    if not versions_dir.exists():
        return []

    rows = []
    for d in sorted(versions_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        if not d.is_dir() or d.is_symlink():
            continue
        files = sorted([f.name for f in d.iterdir() if f.is_file()])
        t = datetime.fromtimestamp(d.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")
        rows.append({"version": d.name, "archived_at": t, "files": files})
    return rows


def rollback(skill_dir: Path, target_version: str) -> None:
    versions_dir = skill_dir / "versions"
    target_version = validate_version(target_version)
    target_dir = safe_child(versions_dir, target_version, kind="version")
    if not target_dir.exists():
        raise FileNotFoundError(f"找不到版本：{target_version}")

    # 回滚前自动备份当前状态
    backup(skill_dir, explicit_version=f"before_rollback_{datetime.now().strftime('%Y%m%d%H%M%S')}")

    restored = 0
    for name in CORE_FILES:
        src = target_dir / name
        if src.exists():
            shutil.copy2(src, skill_dir / name)
            restored += 1

    meta = load_meta(skill_dir)
    meta["version"] = f"{target_version}_restored"
    meta["updated_at"] = utc_now()
    meta["rollback_from"] = target_version
    save_meta(skill_dir, meta)
    print(f"OK: 已回滚到 {target_version}，恢复 {restored} 个文件")


def cleanup(skill_dir: Path, max_keep: int = DEFAULT_MAX_KEEP) -> None:
    if max_keep < 0:
        raise ValueError("max_keep 不能为负数")
    versions_dir = skill_dir / "versions"
    if not versions_dir.exists():
        print("无需清理：versions 目录不存在")
        return

    dirs = [d for d in versions_dir.iterdir() if d.is_dir() and not d.is_symlink()]
    dirs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    to_delete = dirs[max_keep:] if len(dirs) > max_keep else []

    for d in to_delete:
        shutil.rmtree(d)
        print(f"已删除旧版本：{d.name}")
    print(f"OK: 清理完成，保留 {min(len(dirs), max_keep)} 个版本")


def main() -> None:
    parser = argparse.ArgumentParser(description="导师 Skill 版本管理")
    parser.add_argument("--action", required=True, choices=["list", "backup", "rollback", "cleanup"])
    parser.add_argument("--slug", required=True, help="导师 slug")
    parser.add_argument("--base-dir", default="./advisors", help="导师 Skill 根目录")
    parser.add_argument("--version", help="目标版本（rollback 时必填）")
    parser.add_argument("--max-keep", type=int, default=DEFAULT_MAX_KEEP, help="cleanup 保留数量")
    args = parser.parse_args()

    slug = validate_slug(args.slug)
    skill_dir = safe_child(Path(args.base_dir).expanduser(), slug)
    if not skill_dir.exists():
        print(f"错误：目录不存在 {skill_dir}", file=sys.stderr)
        sys.exit(1)

    if args.action == "backup":
        backup(skill_dir)
        return

    if args.action == "list":
        rows = list_versions(skill_dir)
        if not rows:
            print("暂无历史版本")
            return
        print(f"{args.slug} 历史版本：\n")
        for row in rows:
            print(f"  {row['version']}  存档: {row['archived_at']}  文件: {', '.join(row['files'])}")
        return

    if args.action == "rollback":
        if not args.version:
            print("错误：rollback 需要 --version", file=sys.stderr)
            sys.exit(1)
        rollback(skill_dir, args.version)
        return

    if args.action == "cleanup":
        cleanup(skill_dir, max_keep=args.max_keep)


if __name__ == "__main__":
    main()
