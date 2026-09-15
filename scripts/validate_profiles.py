from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / 'references/models/etd/official-grade-profiles.yaml'


def load_registry() -> dict[str, Any]:
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError('Registry must be a mapping')
    return data


def resolve_profile(profile_id: str, registry: dict[str, Any],
                    trail: tuple[str, ...] = ()) -> dict[str, Any]:
    profiles = {item['profile_id']: item for item in registry['profiles']}
    if profile_id in trail:
        raise ValueError('Inheritance cycle: ' + ' -> '.join((*trail, profile_id)))
    current = profiles[profile_id]
    parent = current.get('extends')
    resolved = resolve_profile(parent, registry, (*trail, profile_id)) if parent else {}
    merged = {**resolved, **current}
    include = list(dict.fromkeys([*resolved.get('include_criteria', []),
                                  *current.get('include_criteria', [])]))
    excluded = set(current.get('exclude_criteria', []))
    merged['include_criteria'] = [item for item in include if item not in excluded]
    merged['source_refs'] = list(dict.fromkeys([*resolved.get('source_refs', []),
                                               *current.get('source_refs', [])]))
    return merged


def validate_registry(registry: dict[str, Any]) -> list[str]:
    """Check reference metadata, not evidence or a decision's methodology."""
    errors = []
    profiles = registry.get('profiles')
    sources = registry.get('source_catalog')
    vocabulary = registry.get('criteria_vocabulary')
    if (not isinstance(profiles, list) or not profiles or
            not isinstance(sources, list) or not sources or
            not isinstance(vocabulary, dict)):
        return ['Registry needs profiles, source_catalog, and criteria_vocabulary']
    terms = []
    for values in vocabulary.values():
        if not isinstance(values, list) or not all(isinstance(v, str) and v for v in values):
            return ['Criterion vocabulary must contain lists of non-empty strings']
        terms.extend(values)
    if len(terms) != len(set(terms)):
        errors.append('Duplicate criterion vocabulary')
    source_ids = set()
    for source in sources:
        if not isinstance(source, dict) or not isinstance(source.get('source_id'), str):
            return errors + ['Each source needs a source_id']
        sid = source['source_id']
        if not sid or sid in source_ids:
            errors.append(f'Invalid or duplicate source: {sid}')
        source_ids.add(sid)
        for field in ('title', 'authority', 'url', 'normative_status'):
            if not isinstance(source.get(field), str) or not source[field].strip():
                errors.append(f'Source {sid} needs {field}')
        if not str(source.get('url', '')).startswith('https://'):
            errors.append(f'Source {sid} needs an HTTPS URL')
        if source.get('normative_status') != 'official_grade':
            errors.append(f'Source {sid} must identify its official GRADE provenance')
    profile_ids = set()
    for profile in profiles:
        if not isinstance(profile, dict) or not isinstance(profile.get('profile_id'), str):
            return errors + ['Each profile needs a profile_id']
        pid = profile['profile_id']
        if not pid or pid in profile_ids:
            errors.append(f'Invalid or duplicate profile: {pid}')
        profile_ids.add(pid)
        for field in ('include_criteria', 'exclude_criteria', 'source_refs'):
            values = profile.get(field)
            if not isinstance(values, list) or not all(isinstance(v, str) and v for v in values):
                return errors + [f'{pid}: {field} must be a list of non-empty strings']
            if len(values) != len(set(values)):
                errors.append(f'{pid}: duplicate {field}')
        for field, allowed in [('question_family', {'management', 'test'}),
                               ('perspective', {'individual', 'population'}),
                               ('conclusion_form', {'recommendation', 'decision'})]:
            if profile.get(field) not in allowed:
                errors.append(f'{pid}: invalid {field}')
        include, exclude = set(profile['include_criteria']), set(profile['exclude_criteria'])
        if include & exclude:
            errors.append(f'{pid}: criteria both included and excluded')
        if (include | exclude) - set(terms):
            errors.append(f'{pid}: unknown criterion')
        if not profile['source_refs'] or set(profile['source_refs']) - source_ids:
            errors.append(f'{pid}: missing or unknown source')
        if 'extends' in profile and not isinstance(profile['extends'], str):
            return errors + [f'{pid}: extends must be a string']
    for pid in profile_ids:
        try:
            resolve_profile(pid, registry)
        except (KeyError, ValueError) as exc:
            errors.append(f'{pid}: invalid inheritance: {exc}')
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate official-profile reference metadata only.')
    parser.add_argument('--registry-only', action='store_true', help='Explicit reference-only check (the default).')
    parser.parse_args()
    try:
        errors = validate_registry(load_registry())
    except (ValueError, OSError, yaml.YAMLError) as exc:
        errors = [str(exc)]
    for error in errors:
        print('ERROR PROFILE:', error)
    if not errors:
        print('OK: official-profile reference metadata is internally consistent')
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
