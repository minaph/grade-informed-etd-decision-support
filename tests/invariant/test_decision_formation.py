from __future__ import annotations

import json
from pathlib import Path
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]


class DecisionFormationContractTests(unittest.TestCase):
    def setUp(self):
        self.skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.integration = (ROOT / "references/question-formation.md").read_text(encoding="utf-8")
        self.formation = (ROOT / "skills/decision-structuring/references/workflow.md").read_text(encoding="utf-8")
        self.properties = (ROOT / "skills/decision-structuring/references/formation-properties.md").read_text(encoding="utf-8")

    def test_skill_routes_to_question_formation(self):
        self.assertIn("references/question-formation.md", self.skill)
        self.assertIn("skills/decision-structuring/SKILL.md", self.skill)
        self.assertIn("Reverse Projection", self.skill)

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

    def test_documented_object_preserves_contract(self):
        for text in (self.properties, (ROOT / "README.md").read_text()):
            example = yaml.safe_load(text.split("```yaml\n", 1)[1].split("```", 1)[0])
            self.assertEqual({"context", "questions", "alternatives", "tree_mermaid"}, set(example))
            self.assertEqual(["description", "sensemaking", "objects"], list(example["context"]))
            for question in example["questions"]:
                self.assertEqual({"premise", "splitter", "actions"}, set(question))
                self.assertIsInstance(question["actions"], list)
            for alternative in example["alternatives"]:
                self.assertEqual({"label", "description"}, set(alternative))
            self.assertIsInstance(example["tree_mermaid"], str)

    def test_tree_invocation_and_visibility_belong_to_parent(self):
        self.assertIn("for every structuring pass", self.properties)
        self.assertIn("for every case", self.skill)
        self.assertIn("Show the", self.skill)
        self.assertIn("answer-only or fixed-format", self.skill)

    def test_correction_contract_reprojects_semantic_state(self):
        self.assertIn("ordinary language", self.properties)
        self.assertIn("revise `context` and/or `questions`", self.properties)
        self.assertIn("regenerate `tree_mermaid` and `alternatives`", self.properties)
        self.assertIn("Do not accept direct edits to Mermaid nodes", self.formation)

    def test_epistemic_roles_remain_separate(self):
        for term in ("Narrative Sensemaking", "Research", "Interview", "Preset reference model", "EtD appraisal"):
            self.assertIn(term, self.integration)
        self.assertIn("EtD is therefore a feedback generator for Formation", self.integration)

    def test_information_gathering_selection_and_scheduling_are_separate(self):
        self.assertIn("Research and Interview as peer candidates", self.integration)
        self.assertIn("Queue material Interview prompts", self.integration)
        self.assertIn("Research and Preset review loop", self.integration)
        self.assertIn("then ask the queued Interview questions", self.integration)
        self.assertIn("material later Question", self.integration)
        self.assertIn("depends on its answer", self.integration)
        self.assertIn("not an epistemic", self.integration)
        self.assertIn("ranking of Research over Interview", self.integration)
        self.assertIn("formation-information-gathering-scheduling", (ROOT / "evals/decision-formation-cases.json").read_text(encoding="utf-8"))

    def test_operation_vocabulary_is_not_prematurely_standardized(self):
        self.assertIn("Do not standardize a large mutation language in this release", self.formation)
        for primitive in ("SET_STATE", "SET_LEVEL", "CHALLENGE_S2", "RELAX_BRANCH_NODE"):
            self.assertNotIn(primitive, self.formation)

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
