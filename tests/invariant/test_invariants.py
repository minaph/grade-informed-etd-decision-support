from __future__ import annotations
from pathlib import Path
import hashlib, json, re, sys, unittest, yaml

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from validation_lib import load_record
from validate_schema import validate as validate_schema
from validate_sources import validate as validate_sources
from validate_recommendation import validate as validate_recommendation
from validate_governance import validate as validate_governance

VALIDATORS=(validate_schema,validate_sources,validate_recommendation,validate_governance)

class RepresentativeInvariantTests(unittest.TestCase):
    def test_representative_cases_have_no_errors(self):
        cases=sorted((ROOT/'tests/representative_cases').glob('*.yaml'))
        self.assertGreaterEqual(len(cases),12)
        for case in cases:
            record=load_record(case)
            for validator in VALIDATORS:
                with self.subTest(case=case.name,validator=validator.__module__):
                    result=validator(record)
                    self.assertEqual([],result.errors,'\n'.join(f.render() for f in result.findings))

    def test_template_is_valid_unstamped_draft(self):
        record=load_record(ROOT/'assets/canonical-etd-template.yaml')
        self.assertEqual([],validate_schema(record).errors)
        self.assertEqual([],validate_governance(record).errors)
        self.assertIsNone(record['governance']['created_at'])
        self.assertEqual('generated_by_skill',record['governance']['record_origin'])
        self.assertEqual('draft',record['governance']['review_status'])
        self.assertEqual('not_authorized',record['governance']['formal_grade_claim_authorization']['status'])

    def test_claim_layers_are_separate(self):
        formal=load_record(ROOT/'tests/representative_cases/health-formal-grade-draft.yaml')
        self.assertEqual('requirements_met',formal['governance']['grade_evidence_assessment']['status'])
        self.assertEqual('precheck_passed',formal['governance']['grade_etd_assessment']['status'])
        self.assertEqual('pending_human_review',formal['governance']['formal_grade_claim_authorization']['status'])
        self.assertEqual('draft',formal['governance']['review_status'])

    def test_grade_evidence_can_be_used_in_informed_etd(self):
        record=load_record(ROOT/'tests/representative_cases/health-grade-evidence-informed-etd.yaml')
        self.assertEqual('grade_informed_etd',record['governance']['methodological_profile'])
        self.assertEqual('requirements_met',record['governance']['grade_evidence_assessment']['status'])
        self.assertEqual('not_assessed',record['governance']['grade_etd_assessment']['status'])
        self.assertEqual({'moderate'},{x['final_rating'] for x in record['evidence']['certainty_of_effects']})

    def test_authorized_claim_requires_approved_import(self):
        record=load_record(ROOT/'tests/representative_cases/health-formal-grade-authorized-import.yaml')
        self.assertEqual('imported_approved_record',record['governance']['record_origin'])
        self.assertEqual('human_approved',record['governance']['review_status'])
        self.assertEqual('authorized',record['governance']['formal_grade_claim_authorization']['status'])
        self.assertEqual([],validate_governance(record).errors)

    def test_nonhealth_outcomes_are_not_grade_rated(self):
        for case in (ROOT/'tests/representative_cases').glob('*.yaml'):
            record=load_record(case)
            outcomes={x['outcome_id']:x for x in record['decision_case']['question']['outcomes']}
            for item in record['evidence']['certainty_of_effects']:
                if outcomes[item['outcome_id']]['outcome_type']!='health':
                    self.assertEqual('not_rated',item['final_rating'],case.name)

    def test_contrast_is_explicit_and_used(self):
        for case in (ROOT/'tests/representative_cases').glob('*.yaml'):
            record=load_record(case); active=record['decision_case']['question']['active_contrast_id']
            contrast_ids={x['contrast_id'] for x in record['decision_case']['question']['contrasts']}
            self.assertIn(active,contrast_ids)
            self.assertTrue(all(x['contrast_id']==active for x in record['evidence']['effect_estimates']))
            self.assertTrue(all(x['contrast_id']==active for x in record['evidence']['certainty_of_effects']))

    def test_domain_pack_hash_and_candidates(self):
        pack_candidates={}
        for path in (ROOT/'references').glob('domain-*.yaml'):
            data=yaml.safe_load(path.read_text()); pack_candidates[data['pack_id']]={x['candidate_id'] for x in data['candidates']}
        for case in (ROOT/'tests/representative_cases').glob('*.yaml'):
            record=load_record(case)
            considered={x['pack_id']:x for x in record['adaptation']['domain_packs_considered']}
            for pid,item in considered.items():
                path=next(p for p in (ROOT/'references').glob('domain-*.yaml') if yaml.safe_load(p.read_text())['pack_id']==pid)
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),item['pack_sha256'])
            for candidate in record['adaptation']['candidate_assessments']:
                self.assertIn(candidate['candidate_id'],pack_candidates[candidate['pack_id']])

    def test_schema_has_criterion_specific_definitions_and_neutral_enums(self):
        schema=json.loads((ROOT/'assets/canonical-etd-schema.json').read_text())
        for criterion in ('problem','resources','feasibility'):
            self.assertIn(f'criterion_{criterion}',schema['$defs'])
        for status_def in ('execution_status','assessment_status','review_status','integrity_status'):
            self.assertIn(status_def,schema['$defs'])
        refs={item['$ref'] for item in schema['properties']['criteria']['properties']['problem']['anyOf']}
        self.assertEqual({'#/$defs/criterion_problem','#/$defs/criterion_compact_non_applicable'},refs)
        text=json.dumps(schema,ensure_ascii=False)
        for value in ('評価対象','重要性が低い','十分','限定的','不足','確認済み','合理的に推定','不明'):
            self.assertNotIn(f'"{value}"',text)

    def test_skill_frontmatter_and_security_boundaries(self):
        text=(ROOT/'SKILL.md').read_text(); meta=yaml.safe_load(text.split('---',2)[1])
        self.assertRegex(meta['name'],re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$'))
        self.assertTrue(ROOT.name==meta['name'] or re.fullmatch(r'skill-[a-z0-9]+',ROOT.name))
        self.assertEqual({'name','description'},set(meta)); self.assertIn('Python 3.10+',text); self.assertNotIn('$SKILL_DIR',text)
        self.assertRegex(text,re.compile('untrusted content',re.I)); self.assertRegex(text,re.compile('Never invent',re.I))
        self.assertIn('formal_grade_claim_authorization',text)

if __name__=='__main__': unittest.main()
