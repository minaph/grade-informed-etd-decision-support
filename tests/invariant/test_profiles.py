from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import hashlib
import sys
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from validation_lib import load_record
from validate_profiles import load_registry, resolve_profile, validate as validate_profiles, validate_registry
from validate_schema import validate as validate_schema
from validate_recommendation import validate as validate_recommendation


class ProfileAndSchema31Tests(unittest.TestCase):
    def template(self):
        return load_record(ROOT / "assets" / "canonical-etd-template.yaml")

    def codes(self, result):
        return {finding.code for finding in result.findings}

    def test_registry_and_template_validate(self):
        self.assertEqual([], validate_registry().errors)
        self.assertEqual([], validate_profiles(self.template()).errors)

    def test_individual_profile_inheritance_excludes_population_criteria(self):
        profile = resolve_profile("grade.clinical.individual_recommendation")
        criteria = set(profile["include_criteria"])
        self.assertNotIn("resources", criteria)
        self.assertNotIn("resource_certainty", criteria)
        self.assertNotIn("cost_effectiveness", criteria)
        self.assertNotIn("equity", criteria)
        self.assertIn("acceptability", criteria)
        self.assertIn("feasibility", criteria)

    def test_registry_detects_cycle(self):
        registry = load_registry()
        profiles = {item["profile_id"]: item for item in registry["profiles"]}
        profiles["generic.etd"]["extends"] = "grade.clinical.individual_recommendation"
        profiles["grade.clinical.population_recommendation"]["extends"] = "generic.etd"
        self.assertIn("PROFILE_INHERITANCE_CYCLE", self.codes(validate_registry(registry)))

    def test_registry_detects_include_exclude_conflict(self):
        registry = load_registry()
        profile = registry["profiles"][0]
        profile["include_criteria"] = ["problem"]
        profile["exclude_criteria"] = ["problem"]
        self.assertIn("PROFILE_INCLUDE_EXCLUDE_CONFLICT", self.codes(validate_registry(registry)))

    def test_unknown_profile_is_rejected(self):
        record = self.template()
        record["profile_id"] = "unknown.profile"
        self.assertIn("UNKNOWN_PROFILE_ID", self.codes(validate_profiles(record)))

    def test_compact_non_applicable_criterion_is_valid(self):
        record = self.template()
        record["criteria"]["equity"] = {
            "applicability": {
                "status": "outside_mandate",
                "reason": "The owner has no authority to alter the distributional policy.",
            }
        }
        self.assertEqual([], validate_schema(record).errors)

    def test_compact_applicable_criterion_is_rejected(self):
        record = self.template()
        record["criteria"]["equity"] = {
            "applicability": {
                "status": "applicable",
                "reason": "Material to the decision.",
            }
        }
        self.assertIn("SCHEMA", self.codes(validate_schema(record)))

    def test_nonformal_conclusion_may_omit_grade_direction_and_strength(self):
        record = self.template()
        record["conclusion"]["decision_status"] = "recommendation_formed"
        record["conclusion"]["recommendation"] = {
            "direction": None,
            "strength": None,
            "statement": "Publish the requested implementation artifact after validation.",
            "conditions": [],
        }
        self.assertEqual([], validate_recommendation(record).errors)

    def test_schema_30_cannot_use_schema_31_compact_criterion(self):
        record = self.template()
        record["schema_version"] = "3.0.0"
        record.pop("profile_id")
        record["adaptation"].pop("domain_pack_ids")
        record["adaptation"].pop("domain_pack_use_case")
        record["criteria"]["equity"] = {
            "applicability": {
                "status": "outside_mandate",
                "reason": "Compact syntax belongs to Schema 3.1.",
            }
        }
        self.assertIn("SCHEMA", self.codes(validate_schema(record)))

    def test_legacy_pack_record_can_migrate_by_explicit_detachment(self):
        record = load_record(ROOT / "tests" / "representative_cases" / "organization-clear-benefit.yaml")
        record["schema_version"] = "3.1.0"
        record["profile_id"] = "generic.etd"
        record["adaptation"]["domain_packs_considered"] = []
        record["adaptation"]["candidate_assessments"] = []
        record["adaptation"]["domain_pack_ids"] = []
        record["adaptation"]["domain_pack_use_case"] = None
        self.assertEqual([], validate_schema(record).errors)
        self.assertEqual([], validate_profiles(record).errors)

    def test_declared_pack_ids_must_match_selected_pack(self):
        record = self.template()
        record["adaptation"]["domain_pack_ids"] = ["academic"]
        self.assertIn("DOMAIN_PACK_SELECTION_MISMATCH", self.codes(validate_profiles(record)))

    def pack_record(self, pack_id, decision_type, candidate_ids):
        record = self.template()
        path = ROOT / "references" / f"domain-{pack_id.replace('_', '-')}.yaml"
        pack = yaml.safe_load(path.read_text())
        record["decision_case"]["question"]["decision_type"] = decision_type
        record["adaptation"]["domain_pack_ids"] = [pack_id]
        record["adaptation"]["domain_pack_use_case"] = pack["scope"]["included_use_cases"][0]
        record["evidence"]["sources"] = [{
            "source_id": "case-source",
            "title": "User-provided case specification",
            "source_type": "case_document",
            "citation": "Case specification supplied for the representative test.",
            "date": None,
            "provided_by": "user",
            "doi": None,
            "url": None,
            "accessed_at": None,
            "version": None,
            "jurisdiction": None,
            "locator": None,
        }]
        record["adaptation"]["domain_packs_considered"] = [{
            "pack_id": pack_id,
            "pack_version": pack["version"],
            "pack_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "selected": True,
            "selection_reason": "The initial pack scope matches the case.",
            "case_evidence_refs": [],
        }]
        selected = set(candidate_ids)
        assessments = []
        for candidate in pack["candidates"]:
            candidate_id = candidate["candidate_id"]
            is_selected = candidate_id in selected
            mapping = candidate["core_mapping"]
            if mapping.startswith("additional:"):
                criterion_id = mapping.split(":", 1)[1]
                if is_selected:
                    assessment = deepcopy(record["criteria"]["problem"])
                    record["additional_criteria"].append({
                        "criterion_id": criterion_id,
                        "label": candidate["label"],
                        "category": "other",
                        "assessment": assessment,
                    })
                    record["governance"]["etd_framework"]["added_criteria"].append(criterion_id)
                resulting_path = f"additional_criteria.{criterion_id}"
            else:
                resulting_path = f"criteria.{mapping}"
            assessments.append({
                "candidate_id": candidate_id,
                "pack_id": pack_id,
                "selected": is_selected,
                "selection_reason": "Material to this case." if is_selected else "Not material to this bounded representative case.",
                "case_evidence_refs": ["case-source"] if is_selected else [],
                "resulting_record_paths": [resulting_path] if is_selected else [],
            })
        record["adaptation"]["candidate_assessments"] = assessments
        return record

    def test_academic_pack_multiple_representative_cases(self):
        cases = [
            ["academic.scientific_or_scholarly_value", "academic.feasibility_and_capacity"],
            ["academic.transparency_and_reproducibility", "academic.dissemination_and_use"],
        ]
        for candidates in cases:
            with self.subTest(candidates=candidates):
                record = self.pack_record("academic", "research_governance", candidates)
                self.assertEqual([], validate_schema(record).errors)
                self.assertEqual([], validate_profiles(record).errors)

    def test_software_pack_multiple_representative_cases(self):
        cases = [
            ["software.architectural_quality_tradeoffs", "software.implementation_feasibility"],
            ["software.security_risk", "software.reversibility_and_lock_in"],
        ]
        for candidates in cases:
            with self.subTest(candidates=candidates):
                record = self.pack_record("software_engineering", "product_or_operations", candidates)
                self.assertEqual([], validate_schema(record).errors)
                self.assertEqual([], validate_profiles(record).errors)

    def test_profile_question_and_conclusion_mismatches_are_rejected(self):
        record = self.template()
        record["profile_id"] = "grade.tests.population_recommendation"
        self.assertIn("PROFILE_QUESTION_FAMILY_MISMATCH", self.codes(validate_profiles(record)))

        record = self.template()
        record["profile_id"] = "grade.coverage.decision"
        record["decision_case"]["question"]["decision_type"] = "public_health_recommendation"
        record["decision_case"]["question"]["perspective"] = "population"
        record["governance"]["etd_framework"]["selected_criteria"].extend([
            "resource_certainty", "cost_effectiveness"
        ])
        self.assertIn("PROFILE_CONCLUSION_FORM_MISMATCH", self.codes(validate_profiles(record)))

    def test_required_profile_extensions_need_real_assessments_and_declarations(self):
        record = self.template()
        record["profile_id"] = "grade.clinical.population_recommendation"
        record["decision_case"]["question"]["decision_type"] = "clinical_recommendation"
        record["decision_case"]["question"]["perspective"] = "population"
        record["decision_case"]["question"]["evidence_question_type"] = "health_intervention_comparison"
        record["governance"]["etd_framework"]["selected_criteria"].extend([
            "resource_certainty", "cost_effectiveness"
        ])
        codes = self.codes(validate_profiles(record))
        self.assertIn("PROFILE_EXTENSION_ASSESSMENT_MISSING", codes)
        self.assertIn("PROFILE_EXTENSION_NOT_DECLARED_ADDED", codes)

    def test_registry_detects_duplicate_extension_target(self):
        registry = load_registry()
        profile = next(x for x in registry["profiles"] if x["profile_id"] == "grade.clinical.population_recommendation")
        profile["extension_mappings"]["cost_effectiveness"] = "additional:grade.resource_certainty"
        self.assertIn("PROFILE_EXTENSION_MAPPING_DUPLICATE_TARGET", self.codes(validate_registry(registry)))

    def test_registry_detects_resolved_include_exclude_conflict(self):
        registry = load_registry()
        parent = next(x for x in registry["profiles"] if x["profile_id"] == "grade.clinical.individual_recommendation")
        profile = deepcopy(parent)
        profile["profile_id"] = "test.inherited_conflict"
        profile["extends"] = parent["profile_id"]
        profile["include_criteria"] = ["resources"]
        profile["exclude_criteria"] = []
        registry["profiles"].append(profile)
        self.assertIn("PROFILE_RESOLVED_INCLUDE_EXCLUDE_CONFLICT", self.codes(validate_registry(registry)))

    def test_pack_semantic_bypasses_are_rejected(self):
        record = self.pack_record(
            "academic", "research_governance",
            ["academic.scientific_or_scholarly_value"],
        )
        selected = next(x for x in record["adaptation"]["candidate_assessments"] if x["selected"])
        selected["case_evidence_refs"] = []
        selected["resulting_record_paths"] = ["criteria.missing"]
        codes = self.codes(validate_profiles(record))
        self.assertIn("SELECTED_CANDIDATE_WITHOUT_CASE_EVIDENCE", codes)
        self.assertIn("CANDIDATE_RESULT_PATH_MISSING", codes)
        self.assertIn("CANDIDATE_MAPPING_PATH_MISMATCH", codes)

        selected["pack_id"] = "software_engineering"
        self.assertIn("SELECTED_CANDIDATE_FROM_UNSELECTED_PACK", self.codes(validate_profiles(record)))


if __name__ == "__main__":
    unittest.main()
