import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.path_safety import atomic_write_text
from tools.skill_writer import (
    DEFAULT_METHOD_CORE,
    DEFAULT_PLAYBOOK,
    PLACEHOLDER_METHOD_CORE,
    PLACEHOLDER_PLAYBOOK,
    create_skill,
    update_skill,
)
from tools.validate_skill import parse_frontmatter, validate_skill


REPO_ROOT = Path(__file__).resolve().parents[1]


class SkillWriterTests(unittest.TestCase):
    def create_sample(self, base_dir: Path) -> Path:
        return create_skill(
            base_dir=base_dir,
            slug="advisor-a",
            meta={"name": "A 导", "profile": {"discipline": "计算机"}},
            method_core_content="# Method\n\nmethod sentinel",
            academic_content="# Academic\n\nacademic sentinel",
            persona_content="# Persona\n\npersona sentinel",
            playbook_content="# Playbook\n\nplaybook sentinel",
        )

    def test_generated_skill_uses_portable_frontmatter_and_thin_router(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = self.create_sample(Path(temp_dir))

            validate_skill(skill_dir, require_folder_match=True)
            frontmatter = parse_frontmatter(skill_dir / "SKILL.md")
            self.assertEqual(set(frontmatter), {"name", "description"})
            skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
            self.assertNotIn("academic sentinel", skill_text)
            self.assertIn("academic.md", skill_text)
            meta = json.loads((skill_dir / "meta.json").read_text(encoding="utf-8"))
            self.assertEqual(meta["schema_version"], 2)

    def test_create_refuses_nonempty_target(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "advisor-a"
            target.mkdir()
            (target / "keep.txt").write_text("keep", encoding="utf-8")

            with self.assertRaises(FileExistsError):
                self.create_sample(Path(temp_dir))
            self.assertEqual((target / "keep.txt").read_text(encoding="utf-8"), "keep")

    def test_template_settings_control_missing_content(self):
        cases = [
            ("strict_distill", None, False),
            ("hybrid_distill", None, True),
            ("template_first", None, True),
            ("hybrid_distill", False, False),
            ("strict_distill", True, True),
        ]
        for strategy, setting, enabled in cases:
            with self.subTest(strategy=strategy, setting=setting), tempfile.TemporaryDirectory() as temp_dir:
                skill_dir = create_skill(Path(temp_dir), "advisor-a", {"name": "A 导"},
                    None, "# Academic\nUser evidence", "# Persona\nUser evidence",
                    distill_strategy=strategy, use_template_methodology=setting)
                meta = json.loads((skill_dir / "meta.json").read_text(encoding="utf-8"))
                self.assertEqual(meta["use_template_methodology"], enabled)
                method = (skill_dir / "method_core.md").read_text(encoding="utf-8")
                playbook = (skill_dir / "playbook.md").read_text(encoding="utf-8")
                if enabled:
                    self.assertEqual(method, DEFAULT_METHOD_CORE)
                    self.assertEqual(playbook, DEFAULT_PLAYBOOK.format(mode_label="学术理想型"))
                else:
                    self.assertIn("待补充", method)
                    self.assertIn("待补充", playbook)
                    self.assertNotIn("预蒸馏方法论", method)
                    self.assertNotIn("最小必要改动", playbook)
                validate_skill(skill_dir, require_folder_match=True)

    def test_disabled_templates_preserve_supplied_content(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = create_skill(Path(temp_dir), "advisor-a", {"name": "A 导"},
                "# Method\nConfirmed method", "# Academic", "# Persona",
                playbook_content="# Playbook\nConfirmed strategy",
                distill_strategy="strict_distill", use_template_methodology=False)
            self.assertEqual((skill_dir / "method_core.md").read_text(encoding="utf-8"),
                             "# Method\nConfirmed method")
            self.assertEqual((skill_dir / "playbook.md").read_text(encoding="utf-8"),
                             "# Playbook\nConfirmed strategy")

    def test_cli_strict_distillation_defaults_to_no_templates(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            subprocess.run([sys.executable, str(REPO_ROOT / "tools/skill_writer.py"),
                "--action", "create", "--base-dir", temp_dir, "--slug", "advisor-a",
                "--distill-strategy", "strict_distill"], check=True, capture_output=True)
            skill_dir = Path(temp_dir) / "advisor-a"
            meta = json.loads((skill_dir / "meta.json").read_text(encoding="utf-8"))
            self.assertFalse(meta["use_template_methodology"])
            self.assertIn("待补充", (skill_dir / "method_core.md").read_text(encoding="utf-8"))

    def test_update_strict_distillation_removes_untouched_defaults(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = self.create_sample(Path(temp_dir))
            meta_path = skill_dir / "meta.json"
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            meta["distill_strategy"] = "hybrid_distill"
            meta["use_template_methodology"] = True
            meta_path.write_text(json.dumps(meta), encoding="utf-8")
            atomic_write_text(skill_dir / "method_core.md", DEFAULT_METHOD_CORE)
            atomic_write_text(skill_dir / "playbook.md", DEFAULT_PLAYBOOK.format(mode_label="学术理想型"))

            version = update_skill(skill_dir, distill_strategy="strict_distill")

            updated = json.loads(meta_path.read_text(encoding="utf-8"))
            self.assertEqual(version, "v2")
            self.assertEqual(updated["distill_strategy"], "strict_distill")
            self.assertFalse(updated["use_template_methodology"])
            self.assertIn("待补充", (skill_dir / "method_core.md").read_text(encoding="utf-8"))
            self.assertIn("待补充", (skill_dir / "playbook.md").read_text(encoding="utf-8"))
            skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("strict_distill", skill_text)
            self.assertIn("`disabled`", skill_text)
            validate_skill(skill_dir, require_folder_match=True)

    def test_update_strict_distillation_preserves_edited_method(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = self.create_sample(Path(temp_dir))
            meta_path = skill_dir / "meta.json"
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            meta["distill_strategy"] = "hybrid_distill"
            meta["use_template_methodology"] = True
            meta_path.write_text(json.dumps(meta), encoding="utf-8")
            atomic_write_text(skill_dir / "method_core.md", "# Method\n\nUser confirmed method")

            update_skill(skill_dir, distill_strategy="strict_distill")

            updated = json.loads(meta_path.read_text(encoding="utf-8"))
            self.assertFalse(updated["use_template_methodology"])
            self.assertEqual((skill_dir / "method_core.md").read_text(encoding="utf-8"),
                             "# Method\n\nUser confirmed method")

    def test_update_to_hybrid_fills_untouched_placeholders(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = create_skill(Path(temp_dir), "advisor-a", {"name": "A 导"},
                None, "# Academic", "# Persona", distill_strategy="strict_distill")
            meta_path = skill_dir / "meta.json"
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            self.assertFalse(meta["use_template_methodology"])
            self.assertIn("待补充", (skill_dir / "method_core.md").read_text(encoding="utf-8"))

            update_skill(skill_dir, distill_strategy="hybrid_distill")

            updated = json.loads(meta_path.read_text(encoding="utf-8"))
            self.assertTrue(updated["use_template_methodology"])
            self.assertEqual((skill_dir / "method_core.md").read_text(encoding="utf-8"),
                             DEFAULT_METHOD_CORE)
            self.assertEqual((skill_dir / "playbook.md").read_text(encoding="utf-8"),
                             DEFAULT_PLAYBOOK.format(mode_label="学术理想型"))
            self.assertIn("`enabled`", (skill_dir / "SKILL.md").read_text(encoding="utf-8"))

    def test_explicit_template_setting_overrides_strategy_default(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = self.create_sample(Path(temp_dir))
            meta_path = skill_dir / "meta.json"
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            meta["distill_strategy"] = "hybrid_distill"
            meta["use_template_methodology"] = True
            meta_path.write_text(json.dumps(meta), encoding="utf-8")

            update_skill(skill_dir, distill_strategy="strict_distill",
                         use_template_methodology=True)

            updated = json.loads(meta_path.read_text(encoding="utf-8"))
            self.assertEqual(updated["distill_strategy"], "strict_distill")
            self.assertTrue(updated["use_template_methodology"])
            self.assertIn("`enabled`", (skill_dir / "SKILL.md").read_text(encoding="utf-8"))

    def test_same_strategy_preserves_explicit_template_optout(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = self.create_sample(Path(temp_dir))
            meta_path = skill_dir / "meta.json"
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            meta["distill_strategy"] = "hybrid_distill"
            meta["use_template_methodology"] = False
            meta_path.write_text(json.dumps(meta), encoding="utf-8")
            atomic_write_text(skill_dir / "method_core.md", PLACEHOLDER_METHOD_CORE)
            atomic_write_text(skill_dir / "playbook.md", PLACEHOLDER_PLAYBOOK)

            update_skill(skill_dir, distill_strategy="hybrid_distill")

            updated = json.loads(meta_path.read_text(encoding="utf-8"))
            self.assertFalse(updated["use_template_methodology"])
            self.assertEqual((skill_dir / "method_core.md").read_text(encoding="utf-8"),
                             PLACEHOLDER_METHOD_CORE)

    def test_dry_run_prints_diff_without_modifying_source(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir) / "advisors"
            skill_dir = self.create_sample(base_dir)
            patch = Path(temp_dir) / "patch.md"
            patch.write_text("## New rule\n- evidence-bound", encoding="utf-8")
            before = {
                path.name: path.read_bytes()
                for path in skill_dir.iterdir()
                if path.is_file()
            }

            result = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / "tools" / "skill_writer.py"),
                    "--action",
                    "update",
                    "--base-dir",
                    str(base_dir),
                    "--slug",
                    "advisor-a",
                    "--academic-patch",
                    str(patch),
                    "--distill-strategy",
                    "strict_distill",
                    "--dry-run",
                ],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

            after = {
                path.name: path.read_bytes()
                for path in skill_dir.iterdir()
                if path.is_file()
            }
            self.assertEqual(before, after)
            self.assertIn("DRY RUN", result.stdout)
            self.assertIn("evidence-bound", result.stdout)
            self.assertIn("`disabled`", result.stdout)
            self.assertEqual(list((skill_dir / "versions").iterdir()), [])


if __name__ == "__main__":
    unittest.main()
