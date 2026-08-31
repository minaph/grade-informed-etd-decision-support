from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


class DecisionFormationContractTests(unittest.TestCase):
    def setUp(self):
        self.skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.formation = (ROOT / "references/question-formation.md").read_text(encoding="utf-8")
        self.properties = (ROOT / "references/formation-properties.md").read_text(encoding="utf-8")
        self.schema_text = (ROOT / "assets/canonical-etd-schema.json").read_text(encoding="utf-8")

    def test_skill_routes_to_question_formation(self):
        self.assertIn("references/question-formation.md", self.skill)
        self.assertIn("Reverse Projection", self.skill)
        self.assertIn("Keep Formation state outside Canonical Schema 3.1.0", self.skill)

    def test_questions_and_context_are_primary_semantic_state(self):
        self.assertIn("principal source of truth", self.formation)
        self.assertIn("Questions are the primary meaning unit", self.formation)
        self.assertIn("The Tree is a view of the semantic state, not an independent source of truth", self.formation)

    def test_minimal_property_contract_is_explicit(self):
        for field in ("sensemaking", "context:", "description", "objects", "premise", "splitter", "actions", "alternatives", "tree_mermaid"):
            self.assertIn(field, self.properties)
        self.assertIn("Each Question mapping has exactly these three properties", self.properties)
        self.assertIn("Each alternative mapping has exactly these two properties", self.properties)
        self.assertIn("actions: []", self.properties)
        self.assertIn("only a unique local string", self.properties)
        self.assertIn("`label` as its required property", self.properties)
        self.assertIn("unique local display name", self.properties)

    def test_tree_is_internal_but_visible_for_material_complexity(self):
        self.assertIn("for every request", self.properties)
        self.assertIn("Show the Tree when", self.properties)
        self.assertIn("keep the sketch minimal and", self.properties)
        self.assertIn("answer-only, command-only, fixed-format", self.properties)

    def test_correction_contract_reprojects_semantic_state(self):
        self.assertIn("ordinary language", self.properties)
        self.assertIn("revise `context` and/or `questions`", self.properties)
        self.assertIn("regenerate `tree_mermaid` and `alternatives`", self.properties)
        self.assertIn("Do not accept direct edits to Mermaid nodes", self.formation)

    def test_epistemic_roles_remain_separate(self):
        for term in ("Narrative Sensemaking", "Research", "Interview", "Preset reference model", "EtD appraisal"):
            self.assertIn(term, self.formation)
        self.assertIn("EtD is therefore a feedback generator for Formation", self.formation)

    def test_information_gathering_selection_and_scheduling_are_separate(self):
        self.assertIn("Research and Interview as peer candidates", self.formation)
        self.assertIn("Queue material Interview prompts", self.formation)
        self.assertIn("Research and Preset review loop", self.formation)
        self.assertIn("then ask the queued Interview questions", self.formation)
        self.assertIn("material later Question", self.formation)
        self.assertIn("depends on its answer", self.formation)
        self.assertIn("not an epistemic", self.formation)
        self.assertIn("ranking of Research over Interview", self.formation)
        self.assertIn("Research and Interview are peer candidates", self.properties)
        self.assertIn("queued Interview questions as one coherent batch", self.properties)
        self.assertIn("formation-information-gathering-scheduling", (ROOT / "evals/decision-formation-cases.json").read_text(encoding="utf-8"))

    def test_operation_vocabulary_is_not_prematurely_standardized(self):
        self.assertIn("Do not standardize a large mutation language in this release", self.formation)
        for primitive in ("SET_STATE", "SET_LEVEL", "CHALLENGE_S2", "RELAX_BRANCH_NODE"):
            self.assertNotIn(primitive, self.formation)

    def test_canonical_schema_does_not_gain_formation_tree(self):
        lowered = self.schema_text.lower()
        self.assertNotIn('"question_tree"', lowered)
        self.assertNotIn('"formation_questions"', lowered)
        self.assertNotIn('"formation_context"', lowered)

    def test_formation_evals_cover_activation_and_non_activation(self):
        data = json.loads((ROOT / "evals/decision-formation-cases.json").read_text(encoding="utf-8"))
        cases = data["cases"]
        self.assertTrue(any(case["formation_expected"] for case in cases))
        self.assertTrue(any(not case["formation_expected"] for case in cases))
        categories = {case["category"] for case in cases}
        self.assertIn("reverse_projection", categories)
        self.assertIn("formation_update", categories)
        self.assertIn("overapplication_control", categories)


if __name__ == "__main__":
    unittest.main()
