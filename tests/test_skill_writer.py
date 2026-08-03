import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.skill_writer import create_skill
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


if __name__ == "__main__":
    unittest.main()
