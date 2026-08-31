from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class EvalDefinitionTests(unittest.TestCase):
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
