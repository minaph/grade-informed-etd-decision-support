from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

DOMAIN_REFERENCES = {
    f'references/models/{name}.md'
    for name in ('academic', 'education', 'health', 'organization', 'software-engineering')
}


REQUIRED_OUTPUT_CASES = {
    'narrative-category-repair-ja', 'narrative-event-experience-ja',
    'narrative-term-pragmatics-ja', 'narrative-prior-knowledge-learning-ja',
    'narrative-explicit-briefness-control-ja', 'narrative-command-only-control-ja',
}
REQUIRED_DOMAIN_CASES = {
    'academic_funding_priority', 'academic_staff_allocation',
    'academic_transparency_assessment', 'academic_sharing_method',
    'academic_feasible_low_value', 'academic_high_value_ethics_equity',
    'software_monolith_microservices', 'software_build_managed',
    'software_secure_development', 'software_performance_maintainability',
    'software_lockin_speed', 'software_pilot_full_migration',
    'overapplication_simple_code', 'underapplication_security_migration',
    'academic_exclusion_hiring', 'software_exclusion_ui_visual',
    'cross_domain_school', 'education_participation_learning', 'organization_work_transfer',
}


def validate_coverage(cases: list[dict], id_key: str, required_ids: set[str]) -> list[str]:
    missing = required_ids - {case.get(id_key) for case in cases}
    return [f'Missing behavioral coverage: {sorted(missing)}'] if missing else []


def validate_cases(cases: list[dict], *, id_key: str, required: tuple[str, ...],
                   root: Path = ROOT) -> list[str]:
    if not cases:
        return ['Evaluation suite must not be empty']
    errors = []
    ids = set()
    pairs: dict[str, int] = {}
    for item in cases:
        case_id = item.get(id_key)
        if not isinstance(case_id, str) or not case_id or case_id in ids:
            errors.append(f'Invalid or duplicate case id: {case_id}')
        ids.add(case_id)
        for field in required:
            if not item.get(field):
                errors.append(f'{case_id}: missing {field}')
        assertions = item.get('assertions')
        if assertions is not None and (not isinstance(assertions, list) or not assertions or
                                       not all(isinstance(a, str) and a.strip() for a in assertions)):
            errors.append(f'{case_id}: assertions must be non-empty strings')
        for field in ('files', 'expected_domain_references'):
            for relative in item.get(field, []):
                path = (root / relative).resolve()
                if not path.is_relative_to(root.resolve()) or not path.is_file():
                    errors.append(f'{case_id}: missing or escaped reference: {relative}')
                if field == 'expected_domain_references' and relative not in DOMAIN_REFERENCES:
                    errors.append(f'{case_id}: not a domain reference: {relative}')
        pair = item.get('pair_id')
        if pair:
            pairs[pair] = pairs.get(pair, 0) + 1
    for pair, count in pairs.items():
        if count < 2:
            errors.append(f'Metamorphic pair {pair} needs at least two cases')
    return errors


def main() -> int:
    evals = json.loads((ROOT / 'evals/evals.json').read_text())
    triggers = json.loads((ROOT / 'evals/trigger_queries.json').read_text())
    domain_cases = json.loads((ROOT / 'evals/profile-and-pack-cases.json').read_text())['cases']
    formation = json.loads((ROOT / 'evals/decision-formation-cases.json').read_text())['cases']
    meta = yaml.safe_load((ROOT / 'SKILL.md').read_text().split('---', 2)[1])
    registry = yaml.safe_load((ROOT / 'references/models/etd/official-grade-profiles.yaml').read_text())
    profile_ids = {item['profile_id'] for item in registry['profiles']}
    errors = []
    if evals.get('skill_name') != meta.get('name'):
        errors.append('Eval skill name differs from SKILL.md')
    protocol = evals.get('evaluation_protocol', {})
    if set(protocol.get('comparison_modes', [])) != {'with_skill', 'without_skill'}:
        errors.append('Both comparison modes are required')
    if protocol.get('minimum_repetitions_per_prompt', 0) < 3:
        errors.append('Minimum repetitions must be at least 3')
    errors.extend(validate_cases(evals['evals'], id_key='id',
                                required=('category', 'prompt', 'expected_output', 'assertions')))
    errors.extend(validate_coverage(evals['evals'], 'id', REQUIRED_OUTPUT_CASES))
    errors.extend(validate_cases(domain_cases, id_key='case_id', required=('query', 'assertions')))
    errors.extend(validate_coverage(domain_cases, 'case_id', REQUIRED_DOMAIN_CASES))
    errors.extend(validate_cases(formation, id_key='case_id',
                                required=('category', 'prompt', 'expected_output', 'assertions')))
    errors.extend(validate_cases(triggers, id_key='query', required=('expected_response',)))
    for case in triggers:
        if case.get('reference_profile') and case['reference_profile'] not in profile_ids:
            errors.append(f'Unknown reference profile: {case["reference_profile"]}')
    for case in domain_cases:
        if case.get('pair_id') and not all(case.get(k) for k in
                ('changed_dimension', 'expected_change_targets', 'expected_stable_targets')):
            errors.append(f'Incomplete metamorphic domain case: {case["case_id"]}')
    for case in formation:
        if not isinstance(case.get('formation_expected'), bool):
            errors.append(f'Formation case needs boolean formation_expected: {case["case_id"]}')
    categories = {case['category'] for case in formation}
    if not {'alternative_quality', 'epistemic_role_separation', 'assumption_handling',
            'reverse_projection', 'formation_update', 'overapplication_control'} <= categories:
        errors.append('Missing formation behavior coverage')
    positive = sum(c.get('formation_expected') is True for c in formation)
    negative = sum(c.get('formation_expected') is False for c in formation)
    if positive < 6 or negative < 2:
        errors.append('Formation coverage needs at least six positive and two non-activation cases')
    domains = {path for case in domain_cases for path in case.get('expected_domain_references', [])}
    if not DOMAIN_REFERENCES <= domains:
        errors.append('Missing domain-reference evaluation coverage')
    for error in errors:
        print('ERROR EVAL:', error)
    if not errors:
        print(f'OK: {len(evals["evals"])} output, {len(triggers)} routing, '
              f'{len(domain_cases)} domain, {len(formation)} formation definitions; live execution not implied')
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
