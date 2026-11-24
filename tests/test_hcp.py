import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "hcp"


class HcpCliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.source = self.root / "source"
        self.destination = self.root / "destination"
        self.source.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def run_hcp(self, regex, *extra):
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(self.source), str(self.destination), regex, *extra],
            text=True,
            capture_output=True,
        )

    def test_copies_matching_basenames_and_preserves_hierarchy(self):
        (self.source / "AGENTS.md").write_text("root instructions")
        nested = self.source / "parrtos"
        nested.mkdir()
        (nested / "index.md").write_text("index")
        (nested / "notes.txt").write_text("not selected")

        result = self.run_hcp(r"^(AGENTS\.md|index\.md)$")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.destination / "AGENTS.md").read_text(), "root instructions")
        self.assertEqual((self.destination / "parrtos" / "index.md").read_text(), "index")
        self.assertFalse((self.destination / "parrtos" / "notes.txt").exists())

    def test_basename_matching_applies_at_any_depth(self):
        for folder in ("one", "two/deep"):
            path = self.source / folder
            path.mkdir(parents=True)
            (path / "index.md").write_text(folder)

        result = self.run_hcp(r"index\.md$")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.destination / "one" / "index.md").exists())
        self.assertTrue((self.destination / "two" / "deep" / "index.md").exists())

    def test_dry_run_does_not_create_destination(self):
        (self.source / "keep.txt").write_text("hello")
        result = self.run_hcp(r"\.txt$", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("[DRY-RUN]", result.stdout)
        self.assertFalse(self.destination.exists())

    def test_existing_files_are_overwritten_and_unrelated_files_remain(self):
        (self.source / "a.txt").write_text("new")
        self.destination.mkdir()
        (self.destination / "a.txt").write_text("old")
        (self.destination / "other.txt").write_text("keep")

        result = self.run_hcp(r"\.txt$")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.destination / "a.txt").read_text(), "new")
        self.assertEqual((self.destination / "other.txt").read_text(), "keep")

    def test_spaces_in_names_are_supported(self):
        (self.source / "file with spaces.md").write_text("content")
        result = self.run_hcp(r"\.md$")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.destination / "file with spaces.md").exists())

    def test_invalid_regex_fails(self):
        result = self.run_hcp("[")
        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid regular expression", result.stderr)

    def test_no_matches_returns_zero(self):
        (self.source / "a.txt").write_text("content")
        result = self.run_hcp(r"\.md$")
        self.assertEqual(result.returncode, 0)
        self.assertIn("no matching files", result.stdout)

    def test_equal_or_nested_roots_are_rejected(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(self.source), str(self.source / "out"), ".*"],
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("must not be the same", result.stderr)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks are not supported")
    def test_symlink_files_are_skipped(self):
        real = self.source / "real.txt"
        real.write_text("content")
        link = self.source / "link.txt"
        try:
            link.symlink_to(real)
        except OSError:
            self.skipTest("symlink creation is not permitted")

        result = self.run_hcp(r"\.txt$")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.destination / "real.txt").exists())
        self.assertFalse((self.destination / "link.txt").exists())


if __name__ == "__main__":
    unittest.main()
