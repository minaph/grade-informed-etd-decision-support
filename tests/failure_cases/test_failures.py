from __future__ import annotations
from pathlib import Path
import sys, unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from validation_lib import load_record
from validate_schema import validate as validate_schema
from validate_sources import validate as validate_sources
from validate_recommendation import validate as validate_recommendation
from validate_governance import validate as validate_governance

class FailureCaseTests(unittest.TestCase):
    def codes(self,result): return {f.code for f in result.findings}
    def rec(self,name): return load_record(ROOT/'tests/failure_cases'/name)
    def test_missing_criterion(self): self.assertTrue(validate_schema(self.rec('missing-criterion.yaml')).errors)
    def test_source_reported_without_source(self): self.assertIn('EVIDENCE_STATUS_WITHOUT_SOURCE',self.codes(validate_sources(self.rec('confirmed-without-source.yaml'))))
    def test_conditional_without_conditions(self): self.assertIn('CONDITIONAL_WITHOUT_CONDITIONS',self.codes(validate_recommendation(self.rec('conditional-without-conditions.yaml'))))
    def test_generated_human_approval(self): self.assertIn('GENERATED_RECORD_NOT_DRAFT',self.codes(validate_governance(self.rec('improper-human-approved.yaml'))))
    def test_invalid_grade_precheck(self): self.assertIn('GRADE_EVIDENCE_PRECHECK_MISSING_CAPABILITIES',self.codes(validate_governance(self.rec('invalid-grade-claim.yaml'))))
    def test_formal_nonhealth_scope(self): self.assertIn('FORMAL_GRADE_SCOPE_UNSUPPORTED',self.codes(validate_governance(self.rec('formal-grade-nonhealth.yaml'))))
    def test_grade_rating_outside_supported_health_evidence(self): self.assertIn('GRADE_RATING_OUTSIDE_SUPPORTED_HEALTH_EVIDENCE',self.codes(validate_governance(self.rec('grade-rating-in-informed.yaml'))))
    def test_valid_imported_record(self):
        r=self.rec('valid-imported-approved.yaml'); self.assertEqual([],validate_schema(r).errors); self.assertEqual([],validate_governance(r).errors)
    def test_strong_low_certainty_warning(self): self.assertIn('STRONG_WITH_LOW_CERTAINTY',self.codes(validate_recommendation(self.rec('strong-low-certainty.yaml'))))
    def test_criterion_specific_code(self): self.assertIn('SCHEMA',self.codes(validate_schema(self.rec('criterion-judgment-mismatch.yaml'))))
    def test_duplicate_option(self): self.assertIn('DUPLICATE_OPTION_ID',self.codes(validate_schema(self.rec('duplicate-option-id.yaml'))))
    def test_candidate_unknown_source(self): self.assertIn('UNKNOWN_CANDIDATE_SOURCE',self.codes(validate_schema(self.rec('candidate-unknown-source.yaml'))))
    def test_path_traversal(self): self.assertIn('UNSAFE_LOCAL_ARTIFACT',self.codes(validate_sources(self.rec('path-traversal-artifact.yaml'))))
    def test_formal_human_review_cannot_be_disabled(self): self.assertIn('FORMAL_GRADE_REQUIRES_HUMAN_REVIEW',self.codes(validate_governance(self.rec('formal-human-review-disabled.yaml'))))
    def test_ai_cannot_authorize(self): self.assertIn('AI_GENERATED_RECORD_CANNOT_AUTHORIZE_FORMAL_CLAIM',self.codes(validate_governance(self.rec('ai-authorized-formal-claim.yaml'))))
    def test_requirements_met_needs_method_review(self): self.assertIn('GRADE_EVIDENCE_REQUIREMENTS_MET_WITHOUT_METHOD_REVIEW',self.codes(validate_governance(self.rec('requirements-met-without-method-review.yaml'))))
    def test_unknown_contrast(self): self.assertIn('UNKNOWN_EVIDENCE_CONTRAST',self.codes(validate_schema(self.rec('unknown-contrast.yaml'))))
    def test_formal_requires_benefit_and_harm_roles(self): self.assertIn('GRADE_EVIDENCE_PRECHECK_MISSING_OUTCOME_ROLES',self.codes(validate_governance(self.rec('formal-missing-undesirable-outcome.yaml'))))
    def test_certainty_calculation(self): self.assertIn('CERTAINTY_CALCULATION_MISMATCH',self.codes(validate_governance(self.rec('certainty-calculation-mismatch.yaml'))))
    def test_empty_or_boilerplate_certainty_override_is_rejected(self):
        for override in (
            "override:",
            "override: review required.",
            "override: justification goes here",
            "override: review required now.",
            "override: lorem ipsum dolor sit amet",
            "override: 00000000000000000000",
        ):
            with self.subTest(override=override):
                record=load_record(ROOT/'tests/representative_cases/health-formal-grade-authorized-import.yaml')
                assessment=record['evidence']['certainty_of_effects'][0]
                assessment['final_rating']='high'
                assessment['calculation_or_override']=override
                codes=self.codes(validate_governance(record))
                self.assertIn('CERTAINTY_OVERRIDE_JUSTIFICATION_MISSING',codes)
                self.assertIn('CERTAINTY_CALCULATION_MISMATCH',codes)
    def test_structured_case_specific_certainty_override_is_accepted(self):
        rationales=(
            "The panel applied its prespecified decision threshold because the "
            "case-specific confidence interval remained entirely above the minimum "
            "important benefit.",
            "パネルは事前に定めた最小重要差を適用し、この症例に固有の信頼区間が"
            "意思決定閾値を完全に上回ったため、不精確性による格下げを採用しなかった。",
        )
        for rationale in rationales:
            with self.subTest(rationale=rationale):
                record=load_record(ROOT/'tests/representative_cases/health-formal-grade-authorized-import.yaml')
                assessment=record['evidence']['certainty_of_effects'][0]
                assessment['final_rating']='high'
                assessment['calculation_or_override']=f"override: domains=imprecision; rationale={rationale}"
                codes=self.codes(validate_governance(record))
                self.assertNotIn('CERTAINTY_OVERRIDE_JUSTIFICATION_MISSING',codes)
                self.assertNotIn('CERTAINTY_CALCULATION_MISMATCH',codes)
    def test_certainty_override_length_is_bounded(self):
        record=load_record(ROOT/'tests/representative_cases/health-formal-grade-authorized-import.yaml')
        record['evidence']['certainty_of_effects'][0]['calculation_or_override']=(
            "override: domains=imprecision; rationale=" + ("具体的な症例根拠を記録する。" * 500)
        )
        self.assertIn('SCHEMA',self.codes(validate_schema(record)))
    def test_inline_artifacts_cannot_satisfy_formal_capabilities(self):
        record=load_record(ROOT/'tests/representative_cases/health-formal-grade-authorized-import.yaml')
        for artifact in record['evidence']['artifacts']:
            artifact['reference']='#'
            artifact['verification']['integrity']={'status':'not_checked','sha256':None,'checked_by_type':None}
        self.assertIn('INLINE_ARTIFACT_INELIGIBLE_FOR_CAPABILITIES',self.codes(validate_sources(record)))
        self.assertIn('GRADE_EVIDENCE_REQUIREMENTS_MET_WITHOUT_METHOD_REVIEW',self.codes(validate_governance(record)))
    def test_formal_grade_decision_scope_is_rejected(self):
        record=load_record(ROOT/'tests/representative_cases/health-formal-grade-authorized-import.yaml')
        record['decision_case']['question']['decision_type']='health_system_decision'
        self.assertIn('FORMAL_GRADE_SCOPE_UNSUPPORTED',self.codes(validate_governance(record)))

if __name__=='__main__': unittest.main()
