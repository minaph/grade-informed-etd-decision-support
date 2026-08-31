from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from validation_lib import load_record
from validate_schema import validate as validate_schema
from validate_recommendation import validate as validate_recommendation


class CostMetamorphicTest(unittest.TestCase):
    def test_cost_change_is_local_and_traceable(self):
        base = load_record(ROOT / "tests/metamorphic/base.yaml")
        changed = load_record(ROOT / "tests/metamorphic/increased-cost.yaml")

        self.assertNotEqual(base["criteria"]["resources"], changed["criteria"]["resources"])
        self.assertNotEqual(base["criteria"]["balance_of_effects"], changed["criteria"]["balance_of_effects"])
        self.assertNotEqual(base["conclusion"]["recommendation"], changed["conclusion"]["recommendation"])

        for criterion in base["criteria"]:
            if criterion not in {"resources", "balance_of_effects"}:
                self.assertEqual(base["criteria"][criterion], changed["criteria"][criterion])

        self.assertEqual(base["decision_case"], changed["decision_case"])
        self.assertEqual(base["evidence"], changed["evidence"])
        self.assertIn("費用", changed["conclusion"]["justification"])
        self.assertEqual([], validate_schema(base).errors)
        self.assertEqual([], validate_schema(changed).errors)
        self.assertEqual([], validate_recommendation(base).errors)
        self.assertEqual([], validate_recommendation(changed).errors)


if __name__ == "__main__":
    unittest.main()
