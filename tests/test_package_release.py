from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from package_release import ARCHIVE_ROOT, PackageError, build_archive


class PackageReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "parent"
        self.root.mkdir()
        self.git(self.root, "init", "-b", "main")
        self.git(self.root, "config", "user.email", "test@example.invalid")
        self.git(self.root, "config", "user.name", "Test")

    def git(self, path: Path, *args: str) -> str:
        completed = subprocess.run(
            ["git", "-C", str(path), *args],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return completed.stdout.strip()

    def commit_all(self) -> None:
        self.git(self.root, "add", ".")
        self.git(self.root, "commit", "-m", "Initial")

    def test_packages_tracked_worktree_files_and_excludes_generated_files(self):
        (self.root / "README.md").write_text("committed", encoding="utf-8")
        (self.root / "docs").mkdir()
        (self.root / "docs/guide.md").write_text("guide", encoding="utf-8")
        (self.root / "tests").mkdir()
        (self.root / "tests/test_example.py").write_text("test", encoding="utf-8")
        (self.root / "evals").mkdir()
        (self.root / "evals/case.json").write_text("{}", encoding="utf-8")
        (self.root / "dist").mkdir()
        (self.root / "dist/old.zip").write_text("old", encoding="utf-8")
        (self.root / "build").mkdir()
        (self.root / "build/output.txt").write_text("build", encoding="utf-8")
        (self.root / ".env").write_text("secret", encoding="utf-8")
        (self.root / "release.key").write_text("secret", encoding="utf-8")
        self.commit_all()
        (self.root / "README.md").write_text("worktree", encoding="utf-8")
        (self.root / "untracked.md").write_text("not packaged", encoding="utf-8")

        output = self.root / "dist/release.zip"
        build_archive(self.root, output)

        with zipfile.ZipFile(output) as archive:
            names = set(archive.namelist())
            self.assertEqual(archive.read(f"{ARCHIVE_ROOT}/README.md"), b"worktree")
        self.assertIn(f"{ARCHIVE_ROOT}/docs/guide.md", names)
        self.assertIn(f"{ARCHIVE_ROOT}/tests/test_example.py", names)
        self.assertIn(f"{ARCHIVE_ROOT}/evals/case.json", names)
        for excluded in ("dist/old.zip", "build/output.txt", ".env", "release.key", "untracked.md"):
            self.assertNotIn(f"{ARCHIVE_ROOT}/{excluded}", names)

    def test_packages_initialized_pinned_submodule_recursively(self):
        source = Path(self.temp.name) / "source"
        source.mkdir()
        self.git(source, "init", "-b", "main")
        self.git(source, "config", "user.email", "test@example.invalid")
        self.git(source, "config", "user.name", "Test")
        (source / "SKILL.md").write_text("child", encoding="utf-8")
        self.git(source, "add", ".")
        self.git(source, "commit", "-m", "Initial")
        (self.root / "README.md").write_text("parent", encoding="utf-8")
        self.git(self.root, "add", "README.md")
        self.git(self.root, "-c", "protocol.file.allow=always", "submodule", "add", str(source), "skills/example")
        self.git(self.root, "commit", "-m", "Add submodule")
        child = self.root / "skills/example"
        (child / "untracked.md").write_text("not packaged", encoding="utf-8")

        output = self.root / "release.zip"
        build_archive(self.root, output)

        with zipfile.ZipFile(output) as archive:
            self.assertEqual(archive.read(f"{ARCHIVE_ROOT}/skills/example/SKILL.md"), b"child")
            self.assertNotIn(f"{ARCHIVE_ROOT}/skills/example/untracked.md", archive.namelist())

    def test_failed_submodule_validation_preserves_existing_output(self):
        source = Path(self.temp.name) / "source"
        source.mkdir()
        self.git(source, "init", "-b", "main")
        self.git(source, "config", "user.email", "test@example.invalid")
        self.git(source, "config", "user.name", "Test")
        (source / "SKILL.md").write_text("child", encoding="utf-8")
        self.git(source, "add", ".")
        self.git(source, "commit", "-m", "Initial")
        self.git(self.root, "-c", "protocol.file.allow=always", "submodule", "add", str(source), "skills/example")
        self.git(self.root, "commit", "-m", "Add submodule")
        output = self.root / "release.zip"
        output.write_bytes(b"previous archive")
        self.git(self.root, "submodule", "deinit", "--force", "--", "skills/example")

        with self.assertRaisesRegex(PackageError, "not initialized"):
            build_archive(self.root, output)
        self.assertEqual(output.read_bytes(), b"previous archive")

    def test_rejects_submodule_pin_mismatch(self):
        source = Path(self.temp.name) / "source"
        source.mkdir()
        self.git(source, "init", "-b", "main")
        self.git(source, "config", "user.email", "test@example.invalid")
        self.git(source, "config", "user.name", "Test")
        (source / "SKILL.md").write_text("child", encoding="utf-8")
        self.git(source, "add", ".")
        self.git(source, "commit", "-m", "Initial")
        self.git(self.root, "-c", "protocol.file.allow=always", "submodule", "add", str(source), "skills/example")
        self.git(self.root, "commit", "-m", "Add submodule")
        child = self.root / "skills/example"
        self.git(child, "commit", "--allow-empty", "-m", "Different")

        with self.assertRaisesRegex(PackageError, "pin mismatch"):
            build_archive(self.root, self.root / "release.zip")

    def test_rejects_uncommitted_and_staged_submodule_changes(self):
        source = Path(self.temp.name) / "source"
        source.mkdir()
        self.git(source, "init", "-b", "main")
        self.git(source, "config", "user.email", "test@example.invalid")
        self.git(source, "config", "user.name", "Test")
        (source / "SKILL.md").write_text("child", encoding="utf-8")
        self.git(source, "add", ".")
        self.git(source, "commit", "-m", "Initial")
        self.git(self.root, "-c", "protocol.file.allow=always", "submodule", "add", str(source), "skills/example")
        self.git(self.root, "commit", "-m", "Add submodule")
        child = self.root / "skills/example"

        (child / "SKILL.md").write_text("working tree change", encoding="utf-8")
        with self.assertRaisesRegex(PackageError, "uncommitted tracked changes"):
            build_archive(self.root, self.root / "release.zip")
        self.git(child, "restore", "SKILL.md")

        (child / "SKILL.md").write_text("staged change", encoding="utf-8")
        self.git(child, "add", "SKILL.md")
        with self.assertRaisesRegex(PackageError, "staged changes"):
            build_archive(self.root, self.root / "release.zip")

    def test_rejects_tracked_change_in_nested_submodule(self):
        nested_source = Path(self.temp.name) / "nested-source"
        nested_source.mkdir()
        self.git(nested_source, "init", "-b", "main")
        self.git(nested_source, "config", "user.email", "test@example.invalid")
        self.git(nested_source, "config", "user.name", "Test")
        (nested_source / "SKILL.md").write_text("nested", encoding="utf-8")
        self.git(nested_source, "add", ".")
        self.git(nested_source, "commit", "-m", "Initial")

        source = Path(self.temp.name) / "source"
        source.mkdir()
        self.git(source, "init", "-b", "main")
        self.git(source, "config", "user.email", "test@example.invalid")
        self.git(source, "config", "user.name", "Test")
        (source / "SKILL.md").write_text("child", encoding="utf-8")
        self.git(source, "add", ".")
        self.git(source, "commit", "-m", "Initial")
        self.git(source, "-c", "protocol.file.allow=always", "submodule", "add", str(nested_source), "inner")
        self.git(source, "commit", "-m", "Add nested submodule")

        self.git(self.root, "-c", "protocol.file.allow=always", "submodule", "add", str(source), "skills/example")
        self.git(self.root, "commit", "-m", "Add submodule")
        self.git(self.root, "-c", "protocol.file.allow=always", "submodule", "update", "--init", "--recursive")
        nested = self.root / "skills/example/inner"
        (nested / "SKILL.md").write_text("dirty", encoding="utf-8")

        with self.assertRaisesRegex(PackageError, "uncommitted tracked changes"):
            build_archive(self.root, self.root / "release.zip")

    def test_rejects_symlink_that_escapes_repository(self):
        (self.root / "README.md").write_text("parent", encoding="utf-8")
        outside = Path(self.temp.name) / "outside.txt"
        outside.write_text("outside", encoding="utf-8")
        os.symlink(outside, self.root / "escape")
        self.commit_all()

        with self.assertRaisesRegex(PackageError, "symlink escapes"):
            build_archive(self.root, self.root / "release.zip")

    def test_rejects_output_path_that_is_a_source_file(self):
        (self.root / "source.zip").write_text("source", encoding="utf-8")
        self.commit_all()

        with self.assertRaisesRegex(PackageError, "overwrite a source path"):
            build_archive(self.root, self.root / "source.zip")

    def test_rejects_non_zip_and_git_output_paths(self):
        (self.root / "README.md").write_text("parent", encoding="utf-8")
        self.commit_all()

        with self.assertRaisesRegex(PackageError, "must use a .zip extension"):
            build_archive(self.root, self.root / ".env")
        with self.assertRaisesRegex(PackageError, "inside .git"):
            build_archive(self.root, self.root / ".git/output.zip")


if __name__ == "__main__":
    unittest.main()
