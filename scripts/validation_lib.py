from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable
import json
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "assets" / "canonical-etd-schema.json"
MAX_LOCAL_ARTIFACT_BYTES = 5 * 1024 * 1024
ALLOWED_LOCAL_ARTIFACT_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".json", ".csv", ".pdf"}

STANDARD_CRITERIA = (
    "problem", "desirable_effects", "undesirable_effects", "certainty_of_effects", "values",
    "balance_of_effects", "resources", "equity", "acceptability", "feasibility",
)
FORMAL_GRADE_DECISION_TYPES = {"clinical_recommendation", "public_health_recommendation"}
FORMAL_GRADE_EVIDENCE_QUESTION_TYPE = "health_intervention_comparison"
CERTAINTY_DOMAINS = (
    "risk_of_bias", "inconsistency", "indirectness", "imprecision", "publication_bias",
    "large_effect", "dose_response", "residual_confounding",
)
REQUIRED_GRADE_EVIDENCE_CAPABILITIES = {
    "search_strategy", "study_selection", "risk_of_bias", "synthesis_methods",
    "certainty_domains", "outcome_level_certainty", "desirable_and_undesirable_outcomes",
    "evidence_profile_or_sof",
}
REQUIRED_GRADE_ETD_CAPABILITIES = {"etd_judgments", "recommendation_semantics"}
ALLOWED_JUDGMENTS = {
    "problem": {"unknown", "not_applicable", "problem_not_priority", "problem_probably_priority", "problem_priority"},
    "desirable_effects": {"unknown", "not_applicable", "effect_trivial", "effect_small", "effect_moderate", "effect_large", "effect_varies"},
    "undesirable_effects": {"unknown", "not_applicable", "effect_trivial", "effect_small", "effect_moderate", "effect_large", "effect_varies"},
    "certainty_of_effects": {"unknown", "not_applicable", "certainty_high", "certainty_moderate", "certainty_low", "certainty_very_low", "not_rated", "certainty_varies"},
    "values": {"unknown", "not_applicable", "values_no_important_uncertainty", "values_possible_important_uncertainty", "values_probable_important_uncertainty", "values_important_uncertainty", "values_varies"},
    "balance_of_effects": {"unknown", "not_applicable", "balance_favors_option", "balance_probably_favors_option", "balance_neutral", "balance_probably_favors_comparator", "balance_favors_comparator", "balance_varies"},
    "resources": {"unknown", "not_applicable", "resources_large_savings", "resources_moderate_savings", "resources_negligible", "resources_moderate_costs", "resources_large_costs", "resources_varies"},
    "equity": {"unknown", "not_applicable", "equity_increased", "equity_probably_increased", "equity_no_impact", "equity_probably_reduced", "equity_reduced", "equity_varies"},
    "acceptability": {"unknown", "not_applicable", "acceptability_yes", "acceptability_probably_yes", "acceptability_probably_no", "acceptability_no", "acceptability_varies"},
    "feasibility": {"unknown", "not_applicable", "feasibility_yes", "feasibility_probably_yes", "feasibility_probably_no", "feasibility_no", "feasibility_varies"},
}

@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    path: str = ""
    def render(self) -> str:
        where = f" [{self.path}]" if self.path else ""
        return f"{self.severity.upper()} {self.code}{where}: {self.message}"

@dataclass
class ValidationResult:
    findings: list[Finding] = field(default_factory=list)
    def add(self, severity: str, code: str, message: str, path: str = "") -> None:
        self.findings.append(Finding(severity, code, message, path))
    @property
    def errors(self) -> list[Finding]: return [f for f in self.findings if f.severity == "error"]
    @property
    def warnings(self) -> list[Finding]: return [f for f in self.findings if f.severity == "warning"]
    def extend(self, other: "ValidationResult") -> None: self.findings.extend(other.findings)

def load_record(path_or_obj: str | Path | dict[str, Any]) -> dict[str, Any]:
    if isinstance(path_or_obj, dict): return path_or_obj
    path = Path(path_or_obj)
    with path.open("r", encoding="utf-8") as handle: data = yaml.safe_load(handle)
    if not isinstance(data, dict): raise ValueError(f"Record root must be an object: {path}")
    return data

def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle: return json.load(handle)

def get_path(obj: Any, *keys: str, default: Any = None) -> Any:
    current = obj
    for key in keys:
        if not isinstance(current, dict) or key not in current: return default
        current = current[key]
    return current

def iter_criteria(record: dict[str, Any]) -> Iterable[tuple[str, dict[str, Any], str]]:
    criteria = record.get("criteria", {})
    if isinstance(criteria, dict):
        for name, criterion in criteria.items():
            if isinstance(criterion, dict): yield name, criterion, f"criteria.{name}"
    additional = record.get("additional_criteria", [])
    if isinstance(additional, list):
        for index, item in enumerate(additional):
            if isinstance(item, dict) and isinstance(item.get("assessment"), dict):
                yield f"additional:{item.get('criterion_id', index)}", item["assessment"], f"additional_criteria[{index}].assessment"

def items_at(record: dict[str, Any], *keys: str) -> list[dict[str, Any]]:
    value = get_path(record, *keys, default=[])
    return [x for x in value if isinstance(x, dict)] if isinstance(value, list) else []

def ids_with_duplicates(items: list[dict[str, Any]], field: str) -> tuple[set[str], set[str]]:
    seen: set[str] = set(); dup: set[str] = set()
    for item in items:
        value = item.get(field)
        if not isinstance(value, str): continue
        if value in seen: dup.add(value)
        seen.add(value)
    return seen, dup

def option_ids(record: dict[str, Any]) -> set[str]: return ids_with_duplicates(items_at(record,"decision_case","question","options"),"option_id")[0]
def contrast_ids(record: dict[str, Any]) -> set[str]: return ids_with_duplicates(items_at(record,"decision_case","question","contrasts"),"contrast_id")[0]
def outcome_ids(record: dict[str, Any], important_only: bool=False, health_only: bool=False) -> set[str]:
    result=set()
    for item in items_at(record,"decision_case","question","outcomes"):
        if important_only and item.get("importance") not in {"critical","important"}: continue
        if health_only and item.get("outcome_type") != "health": continue
        if isinstance(item.get("outcome_id"),str): result.add(item["outcome_id"])
    return result
def source_ids(record: dict[str, Any]) -> set[str]: return ids_with_duplicates(items_at(record,"evidence","sources"),"source_id")[0]
def artifact_map(record: dict[str, Any]) -> dict[str,dict[str,Any]]:
    return {x["artifact_id"]:x for x in items_at(record,"evidence","artifacts") if isinstance(x.get("artifact_id"),str)}
def artifact_capabilities(record: dict[str, Any], require_methodological_approval: bool=False, artifact_refs: set[str] | None=None) -> set[str]:
    caps=set()
    for artifact in items_at(record,"evidence","artifacts"):
        if artifact_refs is not None and artifact.get("artifact_id") not in artifact_refs:
            continue
        verification=artifact.get("verification",{})
        integrity=get_path(verification,"integrity","status") == "verified"
        structural=get_path(verification,"structural_completeness","status") == "passed"
        methodological=get_path(verification,"methodological_review","status") == "approved"
        if integrity and structural and (methodological or not require_methodological_approval):
            caps.update(artifact.get("satisfies_requirements",[]) or [])
    return caps

def all_artifact_refs(record: dict[str, Any]) -> list[tuple[str,str]]:
    refs=[]
    for i,item in enumerate(items_at(record,"evidence","certainty_of_effects")):
        refs += [(ref,f"evidence.certainty_of_effects[{i}].artifact_refs") for ref in item.get("artifact_refs",[]) or []]
    for key in ("grade_evidence_assessment","grade_etd_assessment"):
        item=get_path(record,"governance",key,default={})
        refs += [(ref,f"governance.{key}.artifact_refs") for ref in item.get("artifact_refs",[]) or []] if isinstance(item,dict) else []
    return refs

def print_result(result: ValidationResult) -> int:
    for finding in result.findings: print(finding.render())
    if not result.findings: print("OK")
    return 1 if result.errors else 0
