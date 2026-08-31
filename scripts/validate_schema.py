from __future__ import annotations
import argparse
import hashlib
from pathlib import Path
from typing import Any
import yaml
from jsonschema import Draft202012Validator, FormatChecker
from validation_lib import *

SCHEMA=load_json(SCHEMA_PATH)
VALIDATOR=Draft202012Validator(SCHEMA, format_checker=FormatChecker())

def _format_path(parts:list[Any])->str:
    out=""
    for p in parts: out += f"[{p}]" if isinstance(p,int) else (("." if out else "")+str(p))
    return out

def _unique(result:ValidationResult, record:dict[str,Any], path:tuple[str,...], field:str, code:str)->set[str]:
    items=items_at(record,*path); ids,dups=ids_with_duplicates(items,field)
    for value in sorted(dups): result.add("error",code,f"Duplicate {field}: {value}",".".join(path))
    return ids

def validate(record:dict[str,Any])->ValidationResult:
    result=ValidationResult()
    for error in sorted(VALIDATOR.iter_errors(record), key=lambda e:list(e.absolute_path)):
        result.add("error","SCHEMA",error.message,_format_path(list(error.absolute_path)))

    options=_unique(result,record,("decision_case","question","options"),"option_id","DUPLICATE_OPTION_ID")
    contrasts=_unique(result,record,("decision_case","question","contrasts"),"contrast_id","DUPLICATE_CONTRAST_ID")
    outcomes=_unique(result,record,("decision_case","question","outcomes"),"outcome_id","DUPLICATE_OUTCOME_ID")
    sources=_unique(result,record,("evidence","sources"),"source_id","DUPLICATE_SOURCE_ID")
    artifacts=_unique(result,record,("evidence","artifacts"),"artifact_id","DUPLICATE_ARTIFACT_ID")
    _unique(result,record,("evidence","effect_estimates"),"estimate_id","DUPLICATE_ESTIMATE_ID")
    additional=_unique(result,record,("additional_criteria",),"criterion_id","DUPLICATE_ADDITIONAL_CRITERION_ID")
    candidate_ids=_unique(result,record,("adaptation","candidate_assessments"),"candidate_id","DUPLICATE_CANDIDATE_ID")
    for key,field,code in [
        (("conclusion","implementation_conditions"),"item_id","DUPLICATE_ACTION_ID"),
        (("conclusion","stop_or_modify_conditions"),"item_id","DUPLICATE_ACTION_ID"),
        (("conclusion","reassessment_triggers"),"item_id","DUPLICATE_ACTION_ID"),
        (("conclusion","next_actions"),"item_id","DUPLICATE_ACTION_ID"),
        (("conclusion","monitoring"),"indicator_id","DUPLICATE_INDICATOR_ID"),
        (("conclusion","unresolved_uncertainties"),"uncertainty_id","DUPLICATE_UNCERTAINTY_ID")]: _unique(result,record,key,field,code)

    contrast_map={x.get("contrast_id"):x for x in items_at(record,"decision_case","question","contrasts")}
    for i,c in enumerate(items_at(record,"decision_case","question","contrasts")):
        for field in ("focal_option_id","comparator_option_id"):
            if c.get(field) not in options: result.add("error","UNKNOWN_CONTRAST_OPTION",f"Unknown option: {c.get(field)}",f"decision_case.question.contrasts[{i}].{field}")
        if c.get("focal_option_id")==c.get("comparator_option_id"): result.add("error","SELF_CONTRAST","Focal and comparator must differ.",f"decision_case.question.contrasts[{i}]")
    active=get_path(record,"decision_case","question","active_contrast_id")
    if active not in contrasts: result.add("error","UNKNOWN_ACTIVE_CONTRAST",f"Unknown active_contrast_id: {active}","decision_case.question.active_contrast_id")
    if len(items_at(record,"decision_case","question","contrasts")) != 1:
        result.add("error","MULTIPLE_CONTRASTS_IN_RECORD","A Canonical EtD Record must contain exactly one contrast.","decision_case.question.contrasts")

    certainty_keys=set()
    for kind in ("effect_estimates","certainty_of_effects"):
        for i,item in enumerate(items_at(record,"evidence",kind)):
            if item.get("contrast_id") not in contrasts: result.add("error","UNKNOWN_EVIDENCE_CONTRAST",f"Unknown contrast_id: {item.get('contrast_id')}",f"evidence.{kind}[{i}].contrast_id")
            elif item.get("contrast_id") != active: result.add("error","NONACTIVE_EVIDENCE_CONTRAST",f"Evidence must reference the active contrast {active}.",f"evidence.{kind}[{i}].contrast_id")
            if item.get("outcome_id") not in outcomes: result.add("error","UNKNOWN_EVIDENCE_OUTCOME",f"Unknown outcome_id: {item.get('outcome_id')}",f"evidence.{kind}[{i}].outcome_id")
            for j,sid in enumerate(item.get("source_ids",[]) or []):
                if sid not in sources: result.add("error","UNKNOWN_SOURCE_REFERENCE",f"Unknown source_id: {sid}",f"evidence.{kind}[{i}].source_ids[{j}]")
            if kind=="certainty_of_effects":
                key=(item.get("contrast_id"),item.get("outcome_id"))
                if key in certainty_keys: result.add("error","DUPLICATE_CERTAINTY_CONTRAST_OUTCOME",f"Duplicate certainty for {key}",f"evidence.certainty_of_effects[{i}]")
                certainty_keys.add(key)

    for i,a in enumerate(items_at(record,"evidence","artifacts")):
        for j,sid in enumerate(a.get("source_ids",[]) or []):
            if sid not in sources: result.add("error","UNKNOWN_ARTIFACT_SOURCE",f"Unknown source_id: {sid}",f"evidence.artifacts[{i}].source_ids[{j}]")
    for ref,path in all_artifact_refs(record):
        if ref not in artifacts: result.add("error","UNKNOWN_ARTIFACT_REFERENCE",f"Unknown artifact_id: {ref}",path)

    valid_integrated=set(STANDARD_CRITERIA)|{f"additional:{x}" for x in additional}
    for name,criterion,path in iter_criteria(record):
        app=criterion.get("applicability",{}); status=app.get("status"); reason=app.get("reason"); target=app.get("integrated_into")
        if status!="applicable" and not str(reason or "").strip(): result.add("error","APPLICABILITY_REASON_REQUIRED",f"{name} requires a reason.",f"{path}.applicability.reason")
        if status=="integrated_elsewhere" and target not in valid_integrated: result.add("error","INVALID_INTEGRATED_TARGET",f"Unknown integrated_into target: {target}",f"{path}.applicability.integrated_into")
        if status!="integrated_elsewhere" and target is not None: result.add("warning","UNUSED_INTEGRATED_TARGET",f"integrated_into is unused for {status}.",f"{path}.applicability.integrated_into")
        if status!="applicable":
            continue
        if criterion.get("materiality")=="low_materiality" and not str(criterion.get("rationale","")).strip(): result.add("error","LOW_MATERIALITY_REASON_REQUIRED",f"{name} requires a rationale.",f"{path}.rationale")
        if name in ALLOWED_JUDGMENTS and criterion.get("judgment_code") not in ALLOWED_JUDGMENTS[name]: result.add("error","INVALID_CRITERION_JUDGMENT",f"{criterion.get('judgment_code')} is not valid for {name}.",f"{path}.judgment_code")
        basis=criterion.get("evidence_basis",{})
        for j,sid in enumerate(basis.get("source_ids",[]) or []):
            if sid not in sources: result.add("error","UNKNOWN_BASIS_SOURCE",f"Unknown source_id: {sid}",f"{path}.evidence_basis.source_ids[{j}]")
        for j,claim in enumerate(criterion.get("evidence",[]) or []):
            for k,sid in enumerate(claim.get("source_ids",[]) or []):
                if sid not in sources: result.add("error","UNKNOWN_CLAIM_SOURCE",f"Unknown source_id: {sid}",f"{path}.evidence[{j}].source_ids[{k}]")

    pack_files={}
    for pack_path in (ROOT / "references").glob("domain-*.yaml"):
        try:
            pack_data=yaml.safe_load(pack_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(pack_data,dict) and isinstance(pack_data.get("pack_id"),str):
            pack_files[pack_data["pack_id"]]=(pack_path,pack_data)
    pack_items=items_at(record,"adaptation","domain_packs_considered")
    pack_ids={x.get("pack_id") for x in pack_items}
    for i,p in enumerate(pack_items):
        pid=p.get("pack_id")
        for j,sid in enumerate(p.get("case_evidence_refs",[]) or []):
            if sid not in sources: result.add("error","UNKNOWN_PACK_SOURCE",f"Unknown source_id: {sid}",f"adaptation.domain_packs_considered[{i}].case_evidence_refs[{j}]")
        if pid == "none" and p.get("selected") is False:
            continue
        if pid not in pack_files:
            result.add("error","UNKNOWN_DOMAIN_PACK",f"No domain pack file for {pid}.",f"adaptation.domain_packs_considered[{i}].pack_id")
            continue
        pack_path,pack_data=pack_files[pid]
        actual_hash=hashlib.sha256(pack_path.read_bytes()).hexdigest()
        if p.get("pack_sha256") != actual_hash: result.add("error","DOMAIN_PACK_HASH_MISMATCH",f"Hash mismatch for {pid}.",f"adaptation.domain_packs_considered[{i}].pack_sha256")
        if p.get("pack_version") != pack_data.get("version"): result.add("error","DOMAIN_PACK_VERSION_MISMATCH",f"Version mismatch for {pid}.",f"adaptation.domain_packs_considered[{i}].pack_version")
    selected_count=sum(1 for p in pack_items if p.get("selected"))
    if selected_count > 1 and not get_path(record,"adaptation","pack_composition_notes",default=[]):
        result.add("warning","MULTIPLE_PACKS_WITHOUT_COMPOSITION_NOTES","Multiple selected packs should document composition and conflicts.","adaptation.pack_composition_notes")
    for i,c in enumerate(items_at(record,"adaptation","candidate_assessments")):
        pid=c.get("pack_id")
        if pid not in pack_ids: result.add("error","UNKNOWN_CANDIDATE_PACK",f"Candidate references unconsidered pack: {pid}",f"adaptation.candidate_assessments[{i}].pack_id")
        if pid in pack_files:
            valid_candidates={x.get("candidate_id") for x in pack_files[pid][1].get("candidates",[]) if isinstance(x,dict)}
            if c.get("candidate_id") not in valid_candidates: result.add("error","UNKNOWN_DOMAIN_CANDIDATE",f"Unknown candidate_id {c.get('candidate_id')} for pack {pid}.",f"adaptation.candidate_assessments[{i}].candidate_id")
        for j,sid in enumerate(c.get("case_evidence_refs",[]) or []):
            if sid not in sources: result.add("error","UNKNOWN_CANDIDATE_SOURCE",f"Unknown source_id: {sid}",f"adaptation.candidate_assessments[{i}].case_evidence_refs[{j}]")

    # Action item IDs must be unique across all action arrays, not only within each array.
    all_action_ids=[]
    for section in ("implementation_conditions","stop_or_modify_conditions","reassessment_triggers","next_actions"):
        all_action_ids.extend((x.get("item_id"),f"conclusion.{section}") for x in items_at(record,"conclusion",section))
    seen_actions=set()
    for action_id,path in all_action_ids:
        if action_id in seen_actions: result.add("error","DUPLICATE_GLOBAL_ACTION_ID",f"Duplicate action item ID: {action_id}",path)
        seen_actions.add(action_id)

    formed=get_path(record,"conclusion","decision_status")=="recommendation_formed"
    if formed and not str(get_path(record,"conclusion","recommendation","statement",default="")).strip(): result.add("error","EMPTY_RECOMMENDATION_STATEMENT","A formed recommendation needs a statement.","conclusion.recommendation.statement")
    return result

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("record",type=Path); a=p.parse_args()
    try:return print_result(validate(load_record(a.record)))
    except Exception as exc: print(f"ERROR EXECUTION: {exc}"); return 2
if __name__=="__main__": raise SystemExit(main())
