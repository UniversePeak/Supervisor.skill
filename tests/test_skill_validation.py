import tempfile
import unittest
from pathlib import Path

from tools.validate_skill import validate_skill


REPO_ROOT = Path(__file__).resolve().parents[1]


class SkillValidationTests(unittest.TestCase):
    def test_root_skill_is_valid(self):
        validate_skill(REPO_ROOT, expected_name="create-supervisor")

    def test_rejects_legacy_client_specific_frontmatter(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = Path(temp_dir) / "bad-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                "---\nname: bad-skill\ndescription: bad\nuser-invocable: true\n---\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "不兼容"):
                validate_skill(skill_dir)


if __name__ == "__main__":
    unittest.main()
