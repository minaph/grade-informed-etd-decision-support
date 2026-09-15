from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from modeling_dependency import DECISION_PATH, MODELING_PATH, WRITING_PATH, package_files, validate_pinned_skill


class ModelingDependencyTests(unittest.TestCase):
    skill_path = MODELING_PATH

    def validate(self):
        return validate_pinned_skill(self.root, self.skill_path)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "parent"
        self.source = Path(self.temp.name) / "source"
        for path in (self.root, self.source):
            path.mkdir()
            self.git(path, "init", "-b", "main")
            self.git(path, "config", "user.email", "test@example.invalid")
            self.git(path, "config", "user.name", "Test")
        (self.source / "SKILL.md").write_text(
            f'---\nname: {self.skill_path.name}\ndescription: Test skill\n---\n\n[Guide](guide.md)\n'
        )
        (self.source / "guide.md").write_text("# Guide\n")
        self.git(self.source, "add", ".")
        self.git(self.source, "commit", "-m", "Initial")
        self.git(self.root, "-c", "protocol.file.allow=always", "submodule", "add", str(self.source), self.skill_path.as_posix())
        self.child = self.root / self.skill_path

    def git(self, path, *args):
        result = subprocess.run(["git", "-C", str(path), *args], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def test_initialized_pinned_child_and_parent_manifest(self):
        self.assertEqual(self.validate(), [])
        (self.root / "note.md").write_text("parent")
        files = package_files(self.root)
        self.assertEqual(set(files), {"./.gitmodules", "./note.md"})

    def test_missing_initialization(self):
        self.git(self.root, "submodule", "deinit", "--force", "--", self.skill_path.as_posix())
        self.assertTrue(any("not initialized" in e for e in self.validate()))

    def test_dirty_and_untracked_child(self):
        (self.child / "guide.md").write_text("changed")
        self.assertTrue(any("uncommitted" in e for e in self.validate()))
        self.git(self.child, "restore", "guide.md")
        (self.child / "extra.md").write_text("new")
        self.assertTrue(any("untracked" in e for e in self.validate()))

    def test_wrong_commit(self):
        self.git(self.child, "-c", "user.email=test@example.invalid", "-c", "user.name=Test", "commit", "--allow-empty", "-m", "Different")
        self.assertTrue(any("differs" in e for e in self.validate()))

    def test_child_reference_escape_and_missing_file(self):
        (self.child / "guide.md").write_text("[Outside](../../outside.md)\n[Missing](absent.md)\n")
        errors = self.validate()
        self.assertEqual(sum("reference is missing or escapes" in e for e in errors), 2)

    def test_child_frontmatter(self):
        (self.child / "SKILL.md").write_text("---\nname: other\ndescription: Test\n---\n")
        self.assertTrue(any("matching name" in e for e in self.validate()))

    def test_gitlink_required(self):
        self.git(self.root, "rm", "--cached", self.skill_path.as_posix())
        self.assertTrue(any("pinned git submodule" in e for e in self.validate()))

    def test_clone_registration_required(self):
        (self.root / ".gitmodules").write_text("")
        self.assertTrue(any("clone URL" in e for e in self.validate()))


class DecisionDependencyTests(ModelingDependencyTests):
    skill_path = DECISION_PATH


class WritingDependencyTests(ModelingDependencyTests):
    skill_path = WRITING_PATH


if __name__ == "__main__":
    unittest.main()
