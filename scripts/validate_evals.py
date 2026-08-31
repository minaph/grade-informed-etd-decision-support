from __future__ import annotations
import json
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
def main()->int:
    errors=[]
    evals=json.loads((ROOT/'evals/evals.json').read_text())
    triggers=json.loads((ROOT/'evals/trigger_queries.json').read_text())
    profile_cases=json.loads((ROOT/'evals/profile-and-pack-cases.json').read_text())
    formation_cases=json.loads((ROOT/'evals/decision-formation-cases.json').read_text())
    skill_text=(ROOT/'SKILL.md').read_text()
    skill_meta=yaml.safe_load(skill_text.split('---',2)[1]) or {}
    registry=yaml.safe_load((ROOT/'references/official-grade-profiles.yaml').read_text())
    profile_ids={x.get('profile_id') for x in registry.get('profiles',[]) if isinstance(x,dict)}
    pack_candidates={}
    for path in (ROOT/'references').glob('domain-*.yaml'):
        pack=yaml.safe_load(path.read_text())
        if isinstance(pack,dict) and isinstance(pack.get('pack_id'),str):
            pack_candidates[pack['pack_id']]={x.get('candidate_id') for x in pack.get('candidates',[]) if isinstance(x,dict)}
    if evals.get('skill_name')!=skill_meta.get('name'): errors.append('evals.skill_name must equal the SKILL.md frontmatter name')
    protocol=evals.get('evaluation_protocol',{})
    if set(protocol.get('comparison_modes',[]))!={'with_skill','without_skill'}: errors.append('comparison modes must include with_skill and without_skill')
    if protocol.get('minimum_repetitions_per_prompt',0)<3: errors.append('minimum repetitions must be at least 3')
    ids=set(); pairs={}
    for item in evals.get('evals',[]):
        eid=item.get('id')
        if not eid or eid in ids: errors.append(f'invalid or duplicate eval id: {eid}')
        ids.add(eid)
        if not all(item.get(k) for k in ('category','prompt','expected_output','assertions')): errors.append(f'eval {eid} is incomplete')
        if item.get('category')=='metamorphic': pairs.setdefault(item.get('pair_id'),0); pairs[item.get('pair_id')]+=1
        for rel in item.get('files',[]):
            if not (ROOT/rel).exists(): errors.append(f'eval {eid} references missing file: {rel}')
    required_output_evals={
        'narrative-category-repair-ja','narrative-event-experience-ja',
        'narrative-term-pragmatics-ja','narrative-prior-knowledge-learning-ja',
        'narrative-explicit-briefness-control-ja','narrative-command-only-control-ja',
    }
    missing_output_evals=sorted(required_output_evals-ids)
    if missing_output_evals: errors.append(f'missing required narrative output evals: {missing_output_evals}')
    for pair,count in pairs.items():
        if not pair or count<2: errors.append(f'metamorphic pair {pair} needs at least two cases')
    allowed_uses={'narrative_support','canonical_record','formal_grade_precheck'}
    use_counts={name:0 for name in allowed_uses}
    for index,item in enumerate(triggers):
        if 'should_trigger' in item: errors.append(f'output-form case {index} still uses should_trigger')
        use=item.get('expected_use')
        if use not in allowed_uses: errors.append(f'output-form case {index} has invalid expected_use: {use}')
        else: use_counts[use]+=1
        if item.get('expected_profile_id') not in profile_ids: errors.append(f'output-form case {index} has unknown profile')
        for pack_id in item.get('expected_domain_pack_ids',[]):
            if pack_id not in pack_candidates: errors.append(f'output-form case {index} has unknown pack: {pack_id}')
        if use=='formal_grade_precheck' and item.get('formal_grade_expected') is not True:
            errors.append(f'formal case {index} must set formal_grade_expected')
    if use_counts['narrative_support']<6 or use_counts['canonical_record']<6 or use_counts['formal_grade_precheck']<3:
        errors.append(f'output-form coverage is too small: {use_counts}')
    profile_case_ids=set(); profile_pairs={}
    for item in profile_cases.get('cases',[]):
        case_id=item.get('case_id')
        if not case_id or case_id in profile_case_ids: errors.append(f'invalid or duplicate profile/pack case id: {case_id}')
        profile_case_ids.add(case_id)
        required={'case_id','query','expected_use','expected_profile_id','expected_domain_pack_ids','formal_grade_expected','assertions'}
        missing=sorted(required-set(item))
        if missing: errors.append(f'case {case_id} is missing required fields: {missing}')
        if item.get('expected_use') not in allowed_uses: errors.append(f'case {case_id} has invalid expected_use')
        if not isinstance(item.get('assertions'),list) or not item.get('assertions'): errors.append(f'case {case_id} needs assertions')
        pair_id=item.get('pair_id')
        if pair_id: profile_pairs[pair_id]=profile_pairs.get(pair_id,0)+1
        if pair_id and not all(item.get(k) for k in ('changed_dimension','expected_change_targets','expected_stable_targets')):
            errors.append(f'metamorphic case {case_id} is incomplete')
        if not pair_id and 'expected_candidate_criteria' not in item:
            errors.append(f'direct case {case_id} needs expected_candidate_criteria')
        profile_id=item.get('expected_profile_id')
        if profile_id is not None and profile_id not in profile_ids: errors.append(f'case {case_id} has unknown profile: {profile_id}')
        for pack_id in item.get('expected_domain_pack_ids',[]):
            if pack_id not in pack_candidates: errors.append(f'case {case_id} has unknown pack: {pack_id}')
        all_candidates=set().union(*(pack_candidates.get(x,set()) for x in item.get('expected_domain_pack_ids',[])))
        for candidate in item.get('expected_candidate_criteria',[]):
            if candidate not in all_candidates: errors.append(f'case {case_id} has unknown candidate: {candidate}')
    for pair_id,count in profile_pairs.items():
        if count<2: errors.append(f'profile/pack metamorphic pair {pair_id} needs at least two cases')
    formation_ids=set(); formation_positive=0; formation_negative=0
    required_formation_categories={'alternative_quality','epistemic_role_separation','assumption_handling','reverse_projection','formation_update','overapplication_control'}
    seen_formation_categories=set()
    for item in formation_cases.get('cases',[]):
        case_id=item.get('case_id')
        if not case_id or case_id in formation_ids: errors.append(f'invalid or duplicate formation case id: {case_id}')
        formation_ids.add(case_id)
        required={'case_id','category','prompt','formation_expected','expected_output','assertions'}
        missing=sorted(required-set(item))
        if missing: errors.append(f'formation case {case_id} is missing required fields: {missing}')
        if not isinstance(item.get('formation_expected'),bool): errors.append(f'formation case {case_id} needs boolean formation_expected')
        elif item.get('formation_expected'): formation_positive+=1
        else: formation_negative+=1
        if not isinstance(item.get('assertions'),list) or not item.get('assertions'): errors.append(f'formation case {case_id} needs assertions')
        if item.get('category'): seen_formation_categories.add(item.get('category'))
    missing_formation_categories=sorted(required_formation_categories-seen_formation_categories)
    if missing_formation_categories: errors.append(f'missing formation eval categories: {missing_formation_categories}')
    if formation_positive<6 or formation_negative<2: errors.append(f'formation eval coverage is too small: positive={formation_positive}, negative={formation_negative}')
    required_families={
        'academic_funding_priority','academic_staff_allocation','academic_transparency_assessment',
        'academic_sharing_method','academic_feasible_low_value','academic_high_value_ethics_equity',
        'software_monolith_microservices','software_build_managed','software_secure_development',
        'software_performance_maintainability','software_lockin_speed','software_pilot_full_migration',
        'overapplication_simple_code','underapplication_security_migration',
        'academic_exclusion_hiring','software_exclusion_ui_visual',
    }
    missing_families=sorted(required_families-profile_case_ids)
    if missing_families: errors.append(f'missing required profile/pack case families: {missing_families}')
    if errors:
        for e in errors: print('ERROR EVAL:',e)
        return 1
    print(f'OK: {len(ids)} output evals; output forms {use_counts}; {len(profile_case_ids)} profile/pack cases; {len(formation_ids)} formation cases; live execution pending')
    return 0
if __name__=='__main__': raise SystemExit(main())
