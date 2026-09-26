from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
CHILD_SKILLS = (
    "conceptual-modeling",
    "decision-structuring",
    "evidence-based-writing",
)
sys.path.insert(0, str(ROOT / "scripts"))

from package_release import ARCHIVE_ROOT, PackageError, build_archive
from portable_content import PortableContentError


class PackageReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "parent"
        self.root.mkdir()
        self.git(self.root, "init", "-b", "main")
        self.git(self.root, "config", "user.email", "test@example.invalid")
        self.git(self.root, "config", "user.name", "Test")
        (self.root / "SKILL.md").write_bytes((ROOT / "SKILL.md").read_bytes())
        shutil.copytree(ROOT / "references", self.root / "references")
        for name in CHILD_SKILLS:
            self._add_submodule(name)
        self.git(self.root, "add", ".")
        self.git(self.root, "commit", "-m", "Initial")

    def git(self, path: Path, *args: str) -> str:
        completed = subprocess.run(
            ["git", "-C", str(path), *args],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return completed.stdout.strip()

    def _add_submodule(self, name: str) -> None:
        source = Path(self.temp.name) / f"source-{name}"
        source.mkdir()
        self.git(source, "init", "-b", "main")
        self.git(source, "config", "user.email", "test@example.invalid")
        self.git(source, "config", "user.name", "Test")
        shutil.copytree(
            ROOT / "skills" / name,
            source,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(".git"),
        )
        self.git(source, "add", ".")
        self.git(source, "commit", "-m", "Initial")
        self.git(
            self.root,
            "-c",
            "protocol.file.allow=always",
            "submodule",
            "add",
            str(source),
            f"skills/{name}",
        )

    def child(self, name: str) -> Path:
        return self.root / "skills" / name

    def test_packages_runtime_worktree_contents_and_excludes_development_files(self):
        for relative in (
            ".github/workflows/release.yml",
            "docs/notes.md",
            "evals/case.json",
            "scripts/tool.py",
            "tests/test_tool.py",
            "MANIFEST.sha256",
            "requirements.txt",
        ):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("development only", encoding="utf-8")
        self.git(self.root, "add", ".")
        self.git(self.root, "commit", "-m", "Add development files")
        health = self.root / "references/models/health.md"
        health.write_text(health.read_text(encoding="utf-8") + "\nWorktree runtime change.\n", encoding="utf-8")

        output = self.root / "dist/release.zip"
        build_archive(self.root, output)

        with zipfile.ZipFile(output) as archive:
            names = set(archive.namelist())
            prefix = f"{ARCHIVE_ROOT}/"
            self.assertIn(prefix + "SKILL.md", names)
            self.assertIn(prefix + "skills/conceptual-modeling/GUIDE.md", names)
            self.assertIn(prefix + "skills/decision-structuring/GUIDE.md", names)
            self.assertIn(prefix + "skills/evidence-based-writing/GUIDE.md", names)
            self.assertIn(prefix + "references/models/etd/official-grade-profiles.yaml", names)
            self.assertIn(b"Worktree runtime change.", archive.read(prefix + "references/models/health.md"))
        for excluded in (
            ".github/workflows/release.yml",
            "docs/notes.md",
            "evals/case.json",
            "scripts/tool.py",
            "tests/test_tool.py",
            "MANIFEST.sha256",
            "requirements.txt",
        ):
            self.assertNotIn(f"{ARCHIVE_ROOT}/{excluded}", names)
        for name in names:
            self.assertTrue(name.startswith(prefix))
            self.assertIn(Path(name).suffix, {".md", ".yaml"})

    def test_folder_and_flat_layouts_have_the_same_payload(self):
        folder = self.root / "folder.zip"
        flat = self.root / "flat.zip"
        build_archive(self.root, folder, "folder")
        build_archive(self.root, flat, "flat")

        with zipfile.ZipFile(folder) as archive:
            folder_files = {
                name.removeprefix(f"{ARCHIVE_ROOT}/"): archive.read(name)
                for name in archive.namelist()
            }
        with zipfile.ZipFile(flat) as archive:
            flat_files = {name: archive.read(name) for name in archive.namelist()}
        self.assertIn("SKILL.md", flat_files)
        self.assertEqual(folder_files, flat_files)

    def test_rejects_dirty_and_pinned_submodules(self):
        child = self.child("conceptual-modeling")
        skill = child / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8") + "\ndirty\n", encoding="utf-8")
        with self.assertRaisesRegex(PackageError, "uncommitted tracked changes"):
            build_archive(self.root, self.root / "release.zip")
        self.git(child, "restore", "SKILL.md")

        skill.write_text(skill.read_text(encoding="utf-8") + "\nstaged\n", encoding="utf-8")
        self.git(child, "add", "SKILL.md")
        with self.assertRaisesRegex(PackageError, "staged changes"):
            build_archive(self.root, self.root / "release.zip")
        self.git(child, "restore", "--staged", "SKILL.md")
        self.git(child, "restore", "SKILL.md")

        self.git(child, "commit", "--allow-empty", "-m", "Different")
        with self.assertRaisesRegex(PackageError, "pin mismatch"):
            build_archive(self.root, self.root / "release.zip")

    def test_failed_submodule_validation_preserves_existing_output(self):
        output = self.root / "release.zip"
        output.write_bytes(b"previous archive")
        self.git(self.root, "submodule", "deinit", "--force", "--", "skills/conceptual-modeling")

        with self.assertRaisesRegex(PackageError, "not initialized"):
            build_archive(self.root, output)
        self.assertEqual(output.read_bytes(), b"previous archive")

    def test_rejects_output_inside_a_submodule(self):
        output = self.child("conceptual-modeling") / "release.zip"

        with self.assertRaisesRegex(PackageError, "inside a submodule"):
            build_archive(self.root, output)

    def test_rejects_non_zip_and_tracked_output_paths(self):
        with self.assertRaisesRegex(PackageError, "inside .git"):
            build_archive(self.root, self.root / ".git/output.zip")
        with self.assertRaisesRegex(PackageError, "must use a .zip extension"):
            build_archive(self.root, self.root / "SKILL.md")

        tracked = self.root / "source.zip"
        tracked.write_bytes(b"source")
        self.git(self.root, "add", "source.zip")
        self.git(self.root, "commit", "-m", "Track output path")
        with self.assertRaisesRegex(PackageError, "overwrite a source path"):
            build_archive(self.root, tracked)

    def test_rejects_runtime_symlink(self):
        runtime = self.root / "references/runtime-link.md"
        runtime.write_text("tracked", encoding="utf-8")
        self.git(self.root, "add", "references/runtime-link.md")
        self.git(self.root, "commit", "-m", "Add runtime link")
        outside = Path(self.temp.name) / "outside.md"
        outside.write_text("outside", encoding="utf-8")
        runtime.unlink()
        runtime.symlink_to(outside)

        with self.assertRaisesRegex(PackageError, "runtime file cannot be a symlink"):
            build_archive(self.root, self.root / "release.zip")

    def test_transform_failure_preserves_existing_output(self):
        output = self.root / "release.zip"
        output.write_bytes(b"previous archive")
        skill = self.root / "SKILL.md"
        skill.write_text(
            skill.read_text(encoding="utf-8").replace(
                "git submodule update --init --recursive",
                "changed acquisition command",
            ),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(PortableContentError, "transformation anchor changed"):
            build_archive(self.root, output)
        self.assertEqual(output.read_bytes(), b"previous archive")


if __name__ == "__main__":
    unittest.main()
