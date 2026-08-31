from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

from validation_lib import (
    ROOT,
    STANDARD_CRITERIA,
    ValidationResult,
    get_path,
    items_at,
    load_record,
    print_result,
)

REGISTRY_PATH = ROOT / "references" / "official-grade-profiles.yaml"
ALLOWED_NORMATIVE_STATUS = {
    "official_grade",
    "external_standard",
    "external_guidance",
    "external_method",
    "local_extension",
}
PACK_SCOPE_DECISION_TYPES = {
    "academic": {"research_governance"},
    "software_engineering": {"product_or_operations", "organization_policy", "other"},
}


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be an object: {path}")
    return data


def load_registry() -> dict[str, Any]:
    return _load_yaml(REGISTRY_PATH)


def _load_packs() -> dict[str, dict[str, Any]]:
    packs = {}
    for path in (ROOT / "references").glob("domain-*.yaml"):
        pack = _load_yaml(path)
        if isinstance(pack.get("pack_id"), str):
            packs[pack["pack_id"]] = pack
    return packs


def _record_path_exists(record: dict[str, Any], path: str) -> bool:
    if path.startswith("additional_criteria."):
        criterion_id = path.split(".", 1)[1]
        return any(item.get("criterion_id") == criterion_id for item in items_at(record, "additional_criteria"))
    current: Any = record
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return False
        current = current[part]
    return True


def _profile_map(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        item["profile_id"]: item
        for item in registry.get("profiles", [])
        if isinstance(item, dict) and isinstance(item.get("profile_id"), str)
    }


def resolve_profile(
    profile_id: str,
    registry: dict[str, Any] | None = None,
    trail: tuple[str, ...] = (),
) -> dict[str, Any]:
    registry = registry or load_registry()
    profiles = _profile_map(registry)
    if profile_id not in profiles:
        raise KeyError(profile_id)
    if profile_id in trail:
        raise ValueError(" -> ".join((*trail, profile_id)))
    current = profiles[profile_id]
    parent_id = current.get("extends")
    if parent_id:
        resolved = resolve_profile(parent_id, registry, (*trail, profile_id))
    else:
        resolved = {
            "include_criteria": [],
            "extension_mappings": {},
            "source_refs": [],
        }
    merged = dict(resolved)
    merged.update({k: v for k, v in current.items() if k not in {
        "include_criteria", "exclude_criteria", "extension_mappings", "source_refs"
    }})
    criteria = list(dict.fromkeys([
        *resolved.get("include_criteria", []),
        *current.get("include_criteria", []),
    ]))
    excluded = set(current.get("exclude_criteria", []))
    merged["include_criteria"] = [item for item in criteria if item not in excluded]
    merged["exclude_criteria"] = list(dict.fromkeys([
        *resolved.get("exclude_criteria", []),
        *current.get("exclude_criteria", []),
    ]))
    mappings = dict(resolved.get("extension_mappings", {}))
    mappings.update(current.get("extension_mappings", {}))
    merged["extension_mappings"] = {
        key: value for key, value in mappings.items() if key not in excluded
    }
    merged["source_refs"] = list(dict.fromkeys([
        *resolved.get("source_refs", []),
        *current.get("source_refs", []),
    ]))
    merged["profile_id"] = profile_id
    return merged


def validate_registry(registry: dict[str, Any] | None = None) -> ValidationResult:
    result = ValidationResult()
    registry = registry or load_registry()
    profiles = registry.get("profiles", [])
    sources = registry.get("source_catalog", [])
    source_ids = {
        item.get("source_id") for item in sources
        if isinstance(item, dict) and isinstance(item.get("source_id"), str)
    }
    profile_ids: set[str] = set()
    vocabulary = set(get_path(registry, "criteria_vocabulary", "canonical", default=[]))
    extensions = set(get_path(registry, "criteria_vocabulary", "extension", default=[]))
    if vocabulary != set(STANDARD_CRITERIA):
        result.add(
            "error", "PROFILE_CANONICAL_CRITERIA_MISMATCH",
            "Registry canonical criteria must equal the Canonical Record standard slots.",
            "criteria_vocabulary.canonical",
        )
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            result.add("error", "PROFILE_SOURCE_INVALID", "Source must be an object.", f"source_catalog[{index}]")
            continue
        if source.get("normative_status") not in ALLOWED_NORMATIVE_STATUS:
            result.add(
                "error", "PROFILE_SOURCE_NORMATIVE_STATUS_INVALID",
                f"Invalid normative_status: {source.get('normative_status')}",
                f"source_catalog[{index}].normative_status",
            )
    for index, profile in enumerate(profiles):
        if not isinstance(profile, dict) or not isinstance(profile.get("profile_id"), str):
            result.add("error", "PROFILE_ID_MISSING", "Profile needs profile_id.", f"profiles[{index}]")
            continue
        profile_id = profile["profile_id"]
        if profile_id in profile_ids:
            result.add("error", "DUPLICATE_PROFILE_ID", f"Duplicate profile_id: {profile_id}", f"profiles[{index}]")
        profile_ids.add(profile_id)
        include = set(profile.get("include_criteria", []))
        exclude = set(profile.get("exclude_criteria", []))
        if include & exclude:
            result.add(
                "error", "PROFILE_INCLUDE_EXCLUDE_CONFLICT",
                f"Criteria both included and excluded: {sorted(include & exclude)}",
                f"profiles[{index}]",
            )
        for source_ref in profile.get("source_refs", []):
            if source_ref not in source_ids:
                result.add(
                    "error", "UNKNOWN_PROFILE_SOURCE",
                    f"Unknown source_ref: {source_ref}",
                    f"profiles[{index}].source_refs",
                )
    profile_map = _profile_map(registry)
    for profile_id, profile in profile_map.items():
        parent = profile.get("extends")
        if parent and parent not in profile_map:
            result.add("error", "UNKNOWN_PROFILE_PARENT", f"Unknown parent: {parent}", profile_id)
            continue
        try:
            resolved = resolve_profile(profile_id, registry)
        except ValueError as exc:
            result.add("error", "PROFILE_INHERITANCE_CYCLE", f"Inheritance cycle: {exc}", profile_id)
            continue
        resolved_include = set(resolved.get("include_criteria", []))
        resolved_exclude = set(resolved.get("exclude_criteria", []))
        if resolved_include & resolved_exclude:
            result.add(
                "error", "PROFILE_RESOLVED_INCLUDE_EXCLUDE_CONFLICT",
                f"Criteria both included and excluded after inheritance: {sorted(resolved_include & resolved_exclude)}",
                profile_id,
            )
        mappings = resolved.get("extension_mappings", {})
        targets: dict[str, str] = {}
        for criterion in resolved.get("include_criteria", []):
            if criterion not in vocabulary and criterion not in extensions:
                result.add(
                    "error", "UNKNOWN_PROFILE_CRITERION",
                    f"Unknown criterion: {criterion}",
                    profile_id,
                )
            if criterion in extensions and criterion not in mappings:
                result.add(
                    "error", "PROFILE_EXTENSION_UNMAPPED",
                    f"Extension criterion lacks Canonical Record mapping: {criterion}",
                    profile_id,
                )
        for criterion, target in mappings.items():
            if criterion not in extensions or not str(target).startswith("additional:"):
                result.add(
                    "error", "PROFILE_EXTENSION_MAPPING_INVALID",
                    f"Invalid extension mapping {criterion}: {target}",
                    profile_id,
                )
            elif target in targets:
                result.add(
                    "error", "PROFILE_EXTENSION_MAPPING_DUPLICATE_TARGET",
                    f"{criterion} and {targets[target]} map to the same target: {target}",
                    profile_id,
                )
            else:
                targets[target] = criterion
    return result


def validate_domain_packs() -> ValidationResult:
    result = ValidationResult()
    pack_ids: set[str] = set()
    for path in sorted((ROOT / "references").glob("domain-*.yaml")):
        try:
            pack = _load_yaml(path)
        except Exception as exc:
            result.add("error", "DOMAIN_PACK_PARSE_ERROR", str(exc), path.name)
            continue
        pack_id = pack.get("pack_id")
        if not isinstance(pack_id, str):
            result.add("error", "DOMAIN_PACK_ID_MISSING", "pack_id is required.", path.name)
            continue
        if pack_id in pack_ids:
            result.add("error", "DUPLICATE_DOMAIN_PACK_ID", f"Duplicate pack_id: {pack_id}", path.name)
        pack_ids.add(pack_id)
        source_ids = {
            item.get("source_id") for item in pack.get("source_basis", [])
            if isinstance(item, dict)
        }
        if pack_id in {"academic", "software_engineering"}:
            for field in ("version", "status", "scope", "source_basis", "applicability_questions", "candidates", "exclusion_rules", "composition_rules"):
                if field not in pack:
                    result.add("error", "DOMAIN_PACK_FIELD_MISSING", f"{field} is required.", path.name)
            for index, source in enumerate(pack.get("source_basis", [])):
                if source.get("normative_status") not in ALLOWED_NORMATIVE_STATUS:
                    result.add(
                        "error", "DOMAIN_PACK_NORMATIVE_STATUS_INVALID",
                        f"Invalid normative_status: {source.get('normative_status')}",
                        f"{path.name}.source_basis[{index}]",
                    )
            for index, candidate in enumerate(pack.get("candidates", [])):
                for field in ("candidate_id", "candidate_type", "label", "case_question", "selection_rule", "evidence_types", "core_mapping", "source_refs", "adaptation_note"):
                    if field not in candidate:
                        result.add(
                            "error", "DOMAIN_CANDIDATE_FIELD_MISSING",
                            f"{field} is required.", f"{path.name}.candidates[{index}]",
                        )
                for source_ref in candidate.get("source_refs", []):
                    if source_ref not in source_ids:
                        result.add(
                            "error", "UNKNOWN_DOMAIN_SOURCE",
                            f"Unknown source_ref: {source_ref}",
                            f"{path.name}.candidates[{index}].source_refs",
                        )
    return result


def validate(record: dict[str, Any]) -> ValidationResult:
    result = ValidationResult()
    registry = load_registry()
    result.extend(validate_registry(registry))
    result.extend(validate_domain_packs())
    profile_id = record.get("profile_id")
    if record.get("schema_version") == "3.0.0" and not profile_id:
        return result
    profiles = _profile_map(registry)
    if profile_id not in profiles:
        result.add("error", "UNKNOWN_PROFILE_ID", f"Unknown profile_id: {profile_id}", "profile_id")
        return result
    resolved = resolve_profile(profile_id, registry)
    methodological_profile = get_path(record, "governance", "methodological_profile")
    decision_type = get_path(record, "decision_case", "question", "decision_type")
    evidence_question_type = get_path(record, "decision_case", "question", "evidence_question_type")
    if str(profile_id).startswith("grade.") and decision_type not in {
        "clinical_recommendation", "public_health_recommendation",
        "health_system_decision", "health_technology_assessment",
    }:
        result.add(
            "error", "OFFICIAL_PROFILE_NONHEALTH_CASE",
            f"Official GRADE profile is incompatible with decision_type: {decision_type}",
            "decision_case.question.decision_type",
        )
    if methodological_profile == "formal_grade_etd_draft" and resolved.get("status") != "reference":
        result.add(
            "error", "FORMAL_GRADE_REQUIRES_OFFICIAL_PROFILE",
            "formal_grade_etd_draft requires a reference GRADE profile.",
            "profile_id",
        )
    if methodological_profile == "formal_grade_etd_draft" and resolved.get("question_family") != "management":
        result.add(
            "error", "FORMAL_GRADE_PROFILE_UNSUPPORTED",
            "The current formal module supports management intervention profiles, not test profiles.",
            "profile_id",
        )
    if methodological_profile == "formal_grade_etd_draft" and resolved.get("conclusion_form") != "recommendation":
        result.add(
            "error", "FORMAL_GRADE_DECISION_PROFILE_UNSUPPORTED",
            "Current formal GRADE support is limited to recommendation-form profiles.",
            "profile_id",
        )
    expected_perspective = resolved.get("perspective")
    recorded_perspective = get_path(record, "decision_case", "question", "perspective")
    if expected_perspective in {"individual", "population"} and recorded_perspective != expected_perspective:
        result.add(
            "error", "PROFILE_PERSPECTIVE_MISMATCH",
            f"Profile requires perspective '{expected_perspective}', got '{recorded_perspective}'.",
            "decision_case.question.perspective",
        )
    selected = set(get_path(record, "governance", "etd_framework", "selected_criteria", default=[]))
    required_criteria = set(resolved.get("include_criteria", []))
    missing = required_criteria - selected
    for criterion in sorted(missing):
        result.add(
            "error", "PROFILE_REQUIRED_CRITERION_MISSING",
            f"Profile requires selected criterion: {criterion}",
            "governance.etd_framework.selected_criteria",
        )
    forbidden = selected & set(resolved.get("exclude_criteria", []))
    for criterion in sorted(forbidden):
        result.add(
            "error", "PROFILE_EXCLUDED_CRITERION_SELECTED",
            f"Profile excludes selected criterion: {criterion}",
            "governance.etd_framework.selected_criteria",
        )
    additional_ids = {
        item.get("criterion_id") for item in items_at(record, "additional_criteria")
        if isinstance(item.get("criterion_id"), str)
    }
    added_criteria = set(get_path(record, "governance", "etd_framework", "added_criteria", default=[]))
    for criterion, target in resolved.get("extension_mappings", {}).items():
        if criterion not in required_criteria:
            continue
        target_id = str(target).split(":", 1)[1]
        if target_id not in additional_ids:
            result.add(
                "error", "PROFILE_EXTENSION_ASSESSMENT_MISSING",
                f"Required extension {criterion} needs additional_criteria id {target_id}.",
                "additional_criteria",
            )
        if target_id not in added_criteria:
            result.add(
                "error", "PROFILE_EXTENSION_NOT_DECLARED_ADDED",
                f"Required extension target must appear in added_criteria: {target_id}.",
                "governance.etd_framework.added_criteria",
            )
    question_family = resolved.get("question_family")
    if question_family == "test" and evidence_question_type != "diagnostic_or_screening":
        result.add(
            "error", "PROFILE_QUESTION_FAMILY_MISMATCH",
            "A test Reference Profile requires diagnostic_or_screening evidence_question_type.",
            "decision_case.question.evidence_question_type",
        )
    if question_family == "management" and evidence_question_type == "diagnostic_or_screening":
        result.add(
            "error", "PROFILE_QUESTION_FAMILY_MISMATCH",
            "A management Reference Profile cannot be used for a diagnostic_or_screening question.",
            "decision_case.question.evidence_question_type",
        )
    expected_conclusion = resolved.get("conclusion_form")
    recommendation_types = {"clinical_recommendation", "public_health_recommendation"}
    decision_types = {"health_system_decision", "health_technology_assessment"}
    if expected_conclusion == "recommendation" and decision_type in decision_types:
        result.add(
            "error", "PROFILE_CONCLUSION_FORM_MISMATCH",
            f"Recommendation profile conflicts with decision_type: {decision_type}",
            "decision_case.question.decision_type",
        )
    if expected_conclusion == "decision" and decision_type in recommendation_types:
        result.add(
            "error", "PROFILE_CONCLUSION_FORM_MISMATCH",
            f"Decision profile conflicts with decision_type: {decision_type}",
            "decision_case.question.decision_type",
        )
    selected_pack_ids = [
        item.get("pack_id") for item in items_at(record, "adaptation", "domain_packs_considered")
        if item.get("selected")
    ]
    declared_pack_ids = get_path(record, "adaptation", "domain_pack_ids", default=[])
    if selected_pack_ids != declared_pack_ids:
        result.add(
            "error", "DOMAIN_PACK_SELECTION_MISMATCH",
            "domain_pack_ids must equal selected domain_packs_considered in order.",
            "adaptation.domain_pack_ids",
        )
    if len(selected_pack_ids) > 1:
        result.add(
            "error", "MULTIPLE_DOMAIN_PACKS_UNSUPPORTED",
            "Schema 3.1 records may select at most one initial domain pack.",
            "adaptation.domain_pack_ids",
        )
    pack_use_case = get_path(record, "adaptation", "domain_pack_use_case")
    packs = _load_packs()
    if not selected_pack_ids and pack_use_case is not None:
        result.add(
            "error", "DOMAIN_PACK_USE_CASE_WITHOUT_PACK",
            "domain_pack_use_case must be null when no pack is selected.",
            "adaptation.domain_pack_use_case",
        )
    if selected_pack_ids:
        pack = packs.get(selected_pack_ids[0], {})
        included_use_cases = set(get_path(pack, "scope", "included_use_cases", default=[]))
        if pack_use_case not in included_use_cases:
            result.add(
                "error", "DOMAIN_PACK_USE_CASE_OUT_OF_SCOPE",
                f"Use case '{pack_use_case}' is not in the selected pack scope.",
                "adaptation.domain_pack_use_case",
            )
    for pack_id in selected_pack_ids:
        allowed = PACK_SCOPE_DECISION_TYPES.get(pack_id)
        if allowed and decision_type not in allowed:
            result.add(
                "error", "DOMAIN_PACK_SCOPE_MISMATCH",
                f"{pack_id} is outside its initial decision_type scope: {decision_type}",
                "decision_case.question.decision_type",
            )
    assessments = items_at(record, "adaptation", "candidate_assessments")
    selected_pack_set = set(selected_pack_ids)
    for index, assessment in enumerate(assessments):
        if assessment.get("selected") and assessment.get("pack_id") not in selected_pack_set:
            result.add(
                "error", "SELECTED_CANDIDATE_FROM_UNSELECTED_PACK",
                f"Selected candidate uses unselected pack: {assessment.get('pack_id')}",
                f"adaptation.candidate_assessments[{index}].pack_id",
            )
        if not assessment.get("selected"):
            continue
        if not assessment.get("case_evidence_refs"):
            result.add(
                "error", "SELECTED_CANDIDATE_WITHOUT_CASE_EVIDENCE",
                "A selected candidate requires at least one case evidence reference.",
                f"adaptation.candidate_assessments[{index}].case_evidence_refs",
            )
        pack = packs.get(assessment.get("pack_id"), {})
        candidate = next(
            (item for item in pack.get("candidates", []) if item.get("candidate_id") == assessment.get("candidate_id")),
            {},
        )
        expected_mapping = candidate.get("core_mapping")
        expected_path = None
        if isinstance(expected_mapping, str):
            expected_path = (
                f"additional_criteria.{expected_mapping.split(':', 1)[1]}"
                if expected_mapping.startswith("additional:")
                else f"criteria.{expected_mapping}"
            )
        paths = assessment.get("resulting_record_paths", [])
        if not paths:
            result.add(
                "error", "SELECTED_CANDIDATE_WITHOUT_RESULT_PATH",
                "A selected candidate requires at least one resulting record path.",
                f"adaptation.candidate_assessments[{index}].resulting_record_paths",
            )
        for path in paths:
            if not _record_path_exists(record, path):
                result.add(
                    "error", "CANDIDATE_RESULT_PATH_MISSING",
                    f"Resulting record path does not exist: {path}",
                    f"adaptation.candidate_assessments[{index}].resulting_record_paths",
                )
        if expected_path and expected_path not in paths:
            result.add(
                "error", "CANDIDATE_MAPPING_PATH_MISMATCH",
                f"Candidate mapping requires resulting path: {expected_path}",
                f"adaptation.candidate_assessments[{index}].resulting_record_paths",
            )
    for pack_id in selected_pack_ids:
        pack_candidate_ids = {
            item.get("candidate_id") for item in packs.get(pack_id, {}).get("candidates", [])
            if isinstance(item, dict)
        }
        assessed_ids = {
            item.get("candidate_id") for item in assessments if item.get("pack_id") == pack_id
        }
        missing_assessments = sorted(pack_candidate_ids - assessed_ids)
        if missing_assessments:
            result.add(
                "error", "DOMAIN_PACK_CANDIDATES_NOT_ASSESSED",
                f"Selected pack candidates need selection or exclusion reasons: {missing_assessments}",
                "adaptation.candidate_assessments",
            )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record", type=Path, nargs="?")
    parser.add_argument("--registry-only", action="store_true")
    args = parser.parse_args()
    try:
        if args.registry_only or args.record is None:
            result = validate_registry()
            result.extend(validate_domain_packs())
        else:
            result = validate(load_record(args.record))
        return print_result(result)
    except Exception as exc:
        print(f"ERROR EXECUTION: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
