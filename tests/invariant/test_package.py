from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_skill_package import validate_decision_subskill, validate_local_references


class PackageValidationTests(unittest.TestCase):
    def test_decision_subskill_rejects_missing_document(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            child = root / "skills/decision-structuring"
            shutil.copytree(ROOT / "skills/decision-structuring", child)
            self.assertEqual([], validate_decision_subskill(root))
            (child / "references/workflow.md").unlink()
            self.assertTrue(validate_decision_subskill(root))

    def test_decision_subskill_rejects_escaped_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            child = root / "skills/decision-structuring"
            shutil.copytree(ROOT / "skills/decision-structuring", child)
            (root / "outside.md").write_text("outside the reusable skill")
            with (child / "SKILL.md").open("a") as stream:
                stream.write("\n[Outside](../../outside.md)\n")
            self.assertTrue(validate_decision_subskill(root))

    def test_parent_references_reject_missing_or_escaped_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "SKILL.md").write_text("[Guide](guide.md)\n")
            self.assertTrue(validate_local_references(root))
            (root / "guide.md").write_text("Guide")
            self.assertEqual([], validate_local_references(root))
            (root / "SKILL.md").write_text("[Outside](../outside.md)\n")
            self.assertTrue(validate_local_references(root))

    def test_package_validator(self):
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate_skill_package.py")],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
