#!/usr/bin/env python3
"""
导师 Skill 写入与更新工具

支持：
1) create：创建导师 Skill 目录与文件
2) update：增量更新 academic/persona 并自动升版本
3) list：列出已创建导师 Skill
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


SKILL_MD_TEMPLATE = """\
---
name: {slug}
description: {name}，{identity}，{mode_label}
argument-hint: [proposal|paper|meeting|rebuttal|deadline|ethics|career|pragmatic]
user-invocable: true
---

# {name}

{identity}

---

## PART 0：Method Core（预蒸馏方法论）

{method_core_content}

---

## PART A：Academic Style

{academic_content}

---

## PART B：Persona

{persona_content}

---

## PART C：Graduation Playbook

{playbook_content}

---

## 运行规则

1. 先由 PART 0 给出通用方法论框架（任务拆解、优先级、风险分级）
2. 再由 PART B 判断沟通策略（语气、力度、边界）
3. 由 PART A 给出可执行指导（动作、标准、时间点）
4. 按当前模式 `{mode_label}` 进行策略优先级排序
5. 遇到学术伦理风险时，优先执行拒绝 + 替代方案
6. Layer 0 规则优先级最高，不得违背

## 蒸馏策略

- 当前策略：`{distill_strategy}`
- 模板方法论：`{use_template_methodology}`
- 素材充分度：`{material_sufficiency_score}`

## 模式切换

- `/{slug}`：完整模式（Academic + Persona）
- `/{slug} proposal`：开题论证模式
- `/{slug} paper`：论文改稿模式
- `/{slug} meeting`：组会问答模式
- `/{slug} rebuttal`：审稿回复模式
- `/{slug} deadline`：进度规划模式
- `/{slug} ethics`：学术伦理检查
- `/{slug} career`：升学/就业决策建议
- `/{slug} pragmatic`：调用 Part C 的务实场景模板
"""

MODE_LABELS = {
    "academic_ideal": "学术理想型",
    "graduation_first": "毕业优先型（含合理裁缝）",
}

DISTILL_STRATEGIES = {
    "strict_distill": "strict_distill（纯素材蒸馏）",
    "hybrid_distill": "hybrid_distill（素材+预蒸馏模板）",
    "template_first": "template_first（模板优先）",
}

DEFAULT_METHOD_CORE = """# Method Core（预蒸馏方法论）

## 目标
- 在红线内最大化毕业可交付，最小化单点失败风险。

## 通用流程
1. 定义问题：目标、约束、验收标准
2. 任务拆解：必须做 / 可选做 / 放弃项
3. 风险分级：高/中/低并匹配兜底方案
4. 周期复盘：每周评估偏差并调整

## 输出格式
- 本周三步
- 每步验收标准
- 风险与备选路径
"""


DEFAULT_PLAYBOOK = """# Graduation Playbook

## 说明
- 当前模式：{mode_label}
- 原则：在学术伦理与导师红线内，最大化实用性。

## 场景模板
1. 数据表达优化（不造假）
2. 叙事重构（证据先行）
3. 最小必要改动通过审稿
"""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(text: str) -> str:
    text = text.strip()
    if not text:
        return "advisor"

    # 优先尝试中文转拼音
    try:
        from pypinyin import lazy_pinyin  # type: ignore

        parts = lazy_pinyin(text)
        s = "-".join(parts)
    except Exception:
        s = text.lower()
        s = s.replace("_", "-")
        s = re.sub(r"\s+", "-", s)
        s = re.sub(r"[^a-z0-9\-\u4e00-\u9fff]", "", s)

    s = s.lower().replace("_", "-")
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "advisor"


def build_identity(meta: dict) -> str:
    profile = meta.get("profile", {})
    parts = [
        profile.get("school", ""),
        profile.get("discipline", ""),
        profile.get("title", ""),
    ]
    identity = " ".join(p for p in parts if p).strip() or "研究生导师"
    team_size = profile.get("team_size", "")
    direction = profile.get("research_direction", "")
    extras = []
    if team_size:
        extras.append(f"团队规模 {team_size}")
    if direction:
        extras.append(f"方向：{direction}")
    if extras:
        identity += "｜" + "，".join(extras)
    return identity


def normalize_mode(mode: Optional[str]) -> str:
    if mode in MODE_LABELS:
        return mode
    return "academic_ideal"


def normalize_distill_strategy(strategy: Optional[str]) -> str:
    if strategy in DISTILL_STRATEGIES:
        return strategy
    return "hybrid_distill"


def normalize_material_score(score: Optional[str]) -> str:
    try:
        value = int(str(score))
    except Exception:
        value = 60
    value = max(0, min(100, value))
    return str(value)


def create_skill(
    base_dir: Path,
    slug: str,
    meta: dict,
    method_core_content: Optional[str],
    academic_content: str,
    persona_content: str,
    playbook_content: Optional[str] = None,
    working_mode: str = "academic_ideal",
    distill_strategy: str = "hybrid_distill",
    use_template_methodology: bool = True,
    material_sufficiency_score: str = "60",
) -> Path:
    skill_dir = base_dir / slug
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "versions").mkdir(exist_ok=True)
    (skill_dir / "materials").mkdir(exist_ok=True)

    if not method_core_content:
        method_core_content = DEFAULT_METHOD_CORE
    (skill_dir / "method_core.md").write_text(method_core_content, encoding="utf-8")
    (skill_dir / "academic.md").write_text(academic_content, encoding="utf-8")
    (skill_dir / "persona.md").write_text(persona_content, encoding="utf-8")
    mode = normalize_mode(working_mode)
    mode_label = MODE_LABELS[mode]
    distill_strategy = normalize_distill_strategy(distill_strategy)
    score = normalize_material_score(material_sufficiency_score)
    if not playbook_content:
        playbook_content = DEFAULT_PLAYBOOK.format(mode_label=mode_label)
    (skill_dir / "playbook.md").write_text(playbook_content, encoding="utf-8")

    name = meta.get("name", slug)
    identity = build_identity(meta)
    skill_md = SKILL_MD_TEMPLATE.format(
        slug=slug,
        name=name,
        identity=identity,
        method_core_content=method_core_content,
        academic_content=academic_content,
        persona_content=persona_content,
        playbook_content=playbook_content,
        mode_label=mode_label,
        distill_strategy=DISTILL_STRATEGIES[distill_strategy],
        use_template_methodology="enabled" if use_template_methodology else "disabled",
        material_sufficiency_score=score,
    )
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")

    meta = dict(meta)
    meta["name"] = name
    meta["slug"] = slug
    meta.setdefault("profile", {})
    meta.setdefault("tags", {})
    meta.setdefault("sources", [])
    meta.setdefault("corrections_count", 0)
    meta["working_mode"] = mode
    meta["distill_strategy"] = distill_strategy
    meta["use_template_methodology"] = bool(use_template_methodology)
    meta["material_sufficiency_score"] = int(score)
    meta.setdefault("created_at", now_iso())
    meta["updated_at"] = now_iso()
    meta["version"] = "v1"

    (skill_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return skill_dir


def _next_version(current_version: str) -> str:
    m = re.match(r"v(\d+)", current_version)
    if not m:
        return "v2"
    return f"v{int(m.group(1)) + 1}"


def _backup_current(skill_dir: Path, version: str) -> Path:
    versions_dir = skill_dir / "versions"
    versions_dir.mkdir(exist_ok=True)
    backup_dir = versions_dir / version
    if backup_dir.exists():
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_dir = versions_dir / f"{version}_{ts}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    for filename in ("SKILL.md", "method_core.md", "academic.md", "persona.md", "playbook.md", "meta.json"):
        src = skill_dir / filename
        if src.exists():
            shutil.copy2(src, backup_dir / filename)
    return backup_dir


def update_skill(
    skill_dir: Path,
    method_core_patch: Optional[str] = None,
    academic_patch: Optional[str] = None,
    persona_patch: Optional[str] = None,
    playbook_patch: Optional[str] = None,
    working_mode: Optional[str] = None,
    distill_strategy: Optional[str] = None,
    use_template_methodology: Optional[bool] = None,
    material_sufficiency_score: Optional[str] = None,
    correction_target: Optional[str] = None,
    correction_line: Optional[str] = None,
) -> str:
    meta_path = skill_dir / "meta.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"meta.json 不存在：{meta_path}")

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    current_version = meta.get("version", "v1")
    _backup_current(skill_dir, current_version)

    if method_core_patch:
        method_core_path = skill_dir / "method_core.md"
        old = method_core_path.read_text(encoding="utf-8") if method_core_path.exists() else ""
        method_core_path.write_text(old.rstrip() + "\n\n" + method_core_patch.strip() + "\n", encoding="utf-8")

    if academic_patch:
        academic_path = skill_dir / "academic.md"
        old = academic_path.read_text(encoding="utf-8") if academic_path.exists() else ""
        academic_path.write_text(old.rstrip() + "\n\n" + academic_patch.strip() + "\n", encoding="utf-8")

    if persona_patch:
        persona_path = skill_dir / "persona.md"
        old = persona_path.read_text(encoding="utf-8") if persona_path.exists() else ""
        persona_path.write_text(old.rstrip() + "\n\n" + persona_patch.strip() + "\n", encoding="utf-8")

    if playbook_patch:
        playbook_path = skill_dir / "playbook.md"
        old = playbook_path.read_text(encoding="utf-8") if playbook_path.exists() else ""
        playbook_path.write_text(old.rstrip() + "\n\n" + playbook_patch.strip() + "\n", encoding="utf-8")

    if correction_target and correction_line:
        target_map = {
            "method_core": "method_core.md",
            "academic": "academic.md",
            "persona": "persona.md",
            "playbook": "playbook.md",
        }
        target_path = skill_dir / target_map.get(correction_target, "persona.md")
        old = target_path.read_text(encoding="utf-8") if target_path.exists() else ""
        section = "## Correction 记录"
        if section not in old:
            old = old.rstrip() + f"\n\n{section}\n"
        updated = old.rstrip() + "\n" + correction_line.strip() + "\n"
        target_path.write_text(updated, encoding="utf-8")
        meta["corrections_count"] = int(meta.get("corrections_count", 0)) + 1

    if working_mode:
        meta["working_mode"] = normalize_mode(working_mode)
    if distill_strategy:
        meta["distill_strategy"] = normalize_distill_strategy(distill_strategy)
    if use_template_methodology is not None:
        meta["use_template_methodology"] = bool(use_template_methodology)
    if material_sufficiency_score is not None:
        meta["material_sufficiency_score"] = int(normalize_material_score(material_sufficiency_score))

    method_core_path = skill_dir / "method_core.md"
    method_core_content = (
        method_core_path.read_text(encoding="utf-8")
        if method_core_path.exists()
        else DEFAULT_METHOD_CORE
    )
    academic_content = (skill_dir / "academic.md").read_text(encoding="utf-8")
    persona_content = (skill_dir / "persona.md").read_text(encoding="utf-8")
    playbook_path = skill_dir / "playbook.md"
    identity = build_identity(meta)
    mode = normalize_mode(meta.get("working_mode"))
    mode_label = MODE_LABELS[mode]
    playbook_content = (
        playbook_path.read_text(encoding="utf-8")
        if playbook_path.exists()
        else DEFAULT_PLAYBOOK.format(mode_label=mode_label)
    )
    regenerated = SKILL_MD_TEMPLATE.format(
        slug=meta.get("slug", skill_dir.name),
        name=meta.get("name", skill_dir.name),
        identity=identity,
        method_core_content=method_core_content,
        academic_content=academic_content,
        persona_content=persona_content,
        playbook_content=playbook_content,
        mode_label=mode_label,
        distill_strategy=DISTILL_STRATEGIES.get(
            normalize_distill_strategy(meta.get("distill_strategy")),
            DISTILL_STRATEGIES["hybrid_distill"],
        ),
        use_template_methodology="enabled" if bool(meta.get("use_template_methodology", True)) else "disabled",
        material_sufficiency_score=normalize_material_score(meta.get("material_sufficiency_score", 60)),
    )
    (skill_dir / "SKILL.md").write_text(regenerated, encoding="utf-8")

    new_version = _next_version(current_version)
    meta["version"] = new_version
    meta["updated_at"] = now_iso()
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return new_version


def list_supervisors(base_dir: Path) -> list[dict]:
    if not base_dir.exists():
        return []

    result: list[dict] = []
    for d in sorted(base_dir.iterdir()):
        if not d.is_dir():
            continue
        meta_path = d / "meta.json"
        if not meta_path.exists():
            continue
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        result.append(
            {
                "slug": meta.get("slug", d.name),
                "name": meta.get("name", d.name),
                "version": meta.get("version", "v1"),
                "updated_at": meta.get("updated_at", ""),
                "corrections_count": meta.get("corrections_count", 0),
                "identity": build_identity(meta),
                "working_mode": MODE_LABELS.get(meta.get("working_mode", "academic_ideal"), "学术理想型"),
                "distill_strategy": DISTILL_STRATEGIES.get(
                    normalize_distill_strategy(meta.get("distill_strategy")),
                    DISTILL_STRATEGIES["hybrid_distill"],
                ),
                "material_sufficiency_score": int(normalize_material_score(meta.get("material_sufficiency_score", 60))),
            }
        )
    return result


def read_optional_file(path: Optional[str]) -> Optional[str]:
    if not path:
        return None
    p = Path(path).expanduser()
    if not p.exists():
        raise FileNotFoundError(f"文件不存在：{p}")
    try:
        return p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return p.read_text(encoding="utf-8-sig")


def read_json_file(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8-sig")
    return json.loads(raw)


def main() -> None:
    parser = argparse.ArgumentParser(description="导师 Skill 写入工具")
    parser.add_argument("--action", required=True, choices=["create", "update", "list"])
    parser.add_argument("--base-dir", default="./advisors", help="导师 Skill 根目录")

    parser.add_argument("--slug", help="导师 slug")
    parser.add_argument("--name", help="导师名称")
    parser.add_argument("--meta", help="meta.json 路径")

    parser.add_argument("--academic", help="academic.md 内容文件路径")
    parser.add_argument("--persona", help="persona.md 内容文件路径")
    parser.add_argument("--method-core", help="method_core.md 内容文件路径")
    parser.add_argument("--academic-patch", help="academic 增量文件路径")
    parser.add_argument("--persona-patch", help="persona 增量文件路径")
    parser.add_argument("--method-core-patch", help="method_core 增量文件路径")
    parser.add_argument("--mode", choices=["academic_ideal", "graduation_first"], help="工作模式")
    parser.add_argument(
        "--distill-strategy",
        choices=["strict_distill", "hybrid_distill", "template_first"],
        help="蒸馏策略",
    )
    parser.add_argument("--use-template-methodology", choices=["true", "false"], help="是否启用预蒸馏方法论")
    parser.add_argument("--material-score", help="素材充分度评分 0-100")
    parser.add_argument("--playbook", help="playbook.md 内容文件路径")
    parser.add_argument("--playbook-patch", help="playbook 增量文件路径")
    parser.add_argument("--correction-target", choices=["method_core", "academic", "persona", "playbook"])
    parser.add_argument("--correction-line", help="纠偏记录行")

    args = parser.parse_args()
    base_dir = Path(args.base_dir).expanduser()

    if args.action == "list":
        rows = list_supervisors(base_dir)
        if not rows:
            print("暂无已创建导师 Skill")
            return
        print(f"已创建 {len(rows)} 个导师 Skill：\n")
        for row in rows:
            updated = row["updated_at"][:19] if row["updated_at"] else "未知"
            print(f"  [{row['slug']}] {row['name']}")
            print(f"    {row['identity']}")
            print(
                f"    模式: {row['working_mode']}  策略: {row['distill_strategy']}  "
                f"素材分: {row['material_sufficiency_score']}  版本: {row['version']}  "
                f"纠偏: {row['corrections_count']}  更新: {updated}"
            )
            print()
        return

    if args.action == "create":
        if not args.slug and not args.name:
            print("错误：create 需要 --slug 或 --name", file=sys.stderr)
            sys.exit(1)

        meta: dict = {}
        if args.meta:
            meta = read_json_file(Path(args.meta).expanduser())
        if args.name:
            meta["name"] = args.name

        slug = args.slug or slugify(meta.get("name", "advisor"))
        method_core_content = read_optional_file(args.method_core)
        academic_content = read_optional_file(args.academic) or "# Academic Style\n\n[待补充]"
        persona_content = read_optional_file(args.persona) or "# Persona\n\n[待补充]"
        playbook_content = read_optional_file(args.playbook)
        working_mode = normalize_mode(args.mode or meta.get("working_mode"))
        distill_strategy = normalize_distill_strategy(args.distill_strategy or meta.get("distill_strategy"))
        if args.use_template_methodology is not None:
            use_template_methodology = args.use_template_methodology == "true"
        else:
            use_template_methodology = bool(meta.get("use_template_methodology", True))
        material_score = normalize_material_score(args.material_score or meta.get("material_sufficiency_score", 60))

        skill_dir = create_skill(
            base_dir,
            slug,
            meta,
            method_core_content,
            academic_content,
            persona_content,
            playbook_content=playbook_content,
            working_mode=working_mode,
            distill_strategy=distill_strategy,
            use_template_methodology=use_template_methodology,
            material_sufficiency_score=material_score,
        )
        print(f"OK: 导师 Skill 已创建：{skill_dir}")
        print(f"   触发命令：/{slug}")
        print(f"   默认模式：{MODE_LABELS[working_mode]}")
        print(f"   蒸馏策略：{DISTILL_STRATEGIES[distill_strategy]}")
        return

    if args.action == "update":
        if not args.slug:
            print("错误：update 需要 --slug", file=sys.stderr)
            sys.exit(1)
        skill_dir = base_dir / args.slug
        if not skill_dir.exists():
            print(f"错误：未找到目录 {skill_dir}", file=sys.stderr)
            sys.exit(1)

        method_core_patch = read_optional_file(args.method_core_patch)
        academic_patch = read_optional_file(args.academic_patch)
        persona_patch = read_optional_file(args.persona_patch)
        playbook_patch = read_optional_file(args.playbook_patch)
        new_version = update_skill(
            skill_dir=skill_dir,
            method_core_patch=method_core_patch,
            academic_patch=academic_patch,
            persona_patch=persona_patch,
            playbook_patch=playbook_patch,
            working_mode=args.mode,
            distill_strategy=args.distill_strategy,
            use_template_methodology=(None if args.use_template_methodology is None else args.use_template_methodology == "true"),
            material_sufficiency_score=args.material_score,
            correction_target=args.correction_target,
            correction_line=args.correction_line,
        )
        print(f"OK: 已更新到 {new_version}：{skill_dir}")


if __name__ == "__main__":
    main()
