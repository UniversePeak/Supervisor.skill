#!/usr/bin/env python3
"""
素材归一化工具

把多个 txt/md/csv/json 文件整理成一个统一文本，便于后续分析。
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


TEXT_EXTS = {".txt", ".md", ".log", ".yaml", ".yml"}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore").strip()


def read_csv(path: Path) -> str:
    rows = []
    with path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(" | ".join(cell.strip() for cell in row))
    return "\n".join(rows).strip()


def read_json(path: Path) -> str:
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
        return json.dumps(data, ensure_ascii=False, indent=2)
    except json.JSONDecodeError:
        return read_text(path)


def normalize_one(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in TEXT_EXTS:
        content = read_text(path)
    elif ext == ".csv":
        content = read_csv(path)
    elif ext == ".json":
        content = read_json(path)
    else:
        content = read_text(path)

    return (
        f"===== FILE: {path} =====\n"
        f"{content if content else '[EMPTY]'}\n"
        f"===== END FILE: {path.name} =====\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="将多文件归一化为单个文本")
    parser.add_argument("--inputs", nargs="+", required=True, help="输入文件路径列表")
    parser.add_argument("--output", required=True, help="输出文本路径")
    args = parser.parse_args()

    input_paths = [Path(p).expanduser() for p in args.inputs]
    output_path = Path(args.output).expanduser()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    chunks = []
    missing = []
    for path in input_paths:
        if not path.exists():
            missing.append(str(path))
            continue
        if path.is_dir():
            continue
        chunks.append(normalize_one(path))

    header = [
        "# Normalized Materials",
        "",
        f"files_total: {len(input_paths)}",
        f"files_processed: {len(chunks)}",
        f"files_missing: {len(missing)}",
        "",
    ]
    if missing:
        header.append("## Missing Files")
        header.extend(f"- {m}" for m in missing)
        header.append("")

    output = "\n".join(header + chunks)
    output_path.write_text(output, encoding="utf-8")
    print(f"OK: 已生成 {output_path}")
    print(f"处理文件: {len(chunks)}，缺失: {len(missing)}")


if __name__ == "__main__":
    main()
