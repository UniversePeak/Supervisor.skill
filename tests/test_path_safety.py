import tempfile
import unittest
from pathlib import Path

from tools.path_safety import safe_child, validate_slug, validate_version


class PathSafetyTests(unittest.TestCase):
    def test_accepts_portable_slug(self):
        self.assertEqual(validate_slug("advisor-a1"), "advisor-a1")

    def test_rejects_slug_traversal(self):
        for value in ("../outside", "a/b", "..", "UPPER", "trailing-"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_slug(value)

    def test_rejects_version_traversal(self):
        for value in ("../v1", "v1/child", ".."):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_version(value)

    def test_safe_child_stays_inside_base(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            child = safe_child(base, "advisor-a")
            self.assertEqual(child.parent, base.resolve())


if __name__ == "__main__":
    unittest.main()
