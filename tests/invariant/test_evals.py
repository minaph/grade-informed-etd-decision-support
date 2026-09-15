from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest
import tempfile
import json

ROOT = Path(__file__).resolve().parents[2]


sys.path.insert(0, str(ROOT / 'scripts'))
from validate_evals import validate_cases, validate_coverage, REQUIRED_OUTPUT_CASES, REQUIRED_DOMAIN_CASES


class EvalDefinitionTests(unittest.TestCase):
    def test_empty_suite_is_rejected(self):
        self.assertTrue(validate_cases([], id_key="id", required=("prompt",)))

    def test_required_behavior_cannot_be_silently_removed(self):
        for file, collection, key, required in (
            ("evals.json", "evals", "id", REQUIRED_OUTPUT_CASES),
            ("profile-and-pack-cases.json", "cases", "case_id", REQUIRED_DOMAIN_CASES),
        ):
            cases = json.loads((ROOT / "evals" / file).read_text())[collection]
            self.assertEqual([], validate_coverage(cases, key, required))
            for removed in required:
                with self.subTest(file=file, removed=removed):
                    reduced = [case for case in cases if case[key] != removed]
                    self.assertTrue(validate_coverage(reduced, key, required))

    def test_duplicate_case_and_incomplete_pair(self):
        case = {"id": "sample", "prompt": "Compare", "pair_id": "cost"}
        self.assertTrue(validate_cases([case, case], id_key="id", required=("prompt",)))
        self.assertTrue(validate_cases([case], id_key="id", required=("prompt",)))

    def test_missing_or_escaped_input_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            case = {"id": "sample", "prompt": "Compare", "files": ["evidence.md"]}
            self.assertTrue(validate_cases([case], id_key="id", required=("prompt",), root=root))
            (root / "evidence.md").write_text("Case evidence")
            self.assertEqual([], validate_cases([case], id_key="id", required=("prompt",), root=root))
            case["files"] = ["../evidence.md"]
            self.assertTrue(validate_cases([case], id_key="id", required=("prompt",), root=root))

    def test_eval_definitions_validate(self):
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate_evals.py")],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
