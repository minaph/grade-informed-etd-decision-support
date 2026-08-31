from __future__ import annotations
import argparse, hashlib
from pathlib import Path
from urllib.parse import urlparse
from validation_lib import *

def _safe_local_path(reference:str)->tuple[Path|None,str|None]:
    rel=reference[5:]
    if not rel: return None,"Empty file reference."
    candidate=(ROOT/rel).resolve()
    root=ROOT.resolve()
    try: candidate.relative_to(root)
    except ValueError: return None,"Local artifact escapes the skill root."
    if candidate.is_symlink(): return None,"Symbolic-link artifacts are not allowed."
    return candidate,None

def validate(record:dict)->ValidationResult:
    result=ValidationResult(); sources=source_ids(record)
    for name,criterion,path in iter_criteria(record):
        for i,claim in enumerate(criterion.get("evidence",[]) or []):
            refs=claim.get("source_ids",[]) or []; status=claim.get("status")
            if status in {"source_reported","verified_against_source","corroborated"} and not refs: result.add("error","EVIDENCE_STATUS_WITHOUT_SOURCE",f"{status} requires source_ids.",f"{path}.evidence[{i}]")
            if status=="verified_against_source" and claim.get("support_relation",{}).get("reviewer_assessment")=="not_assessed": result.add("error","VERIFIED_WITHOUT_SUPPORT_ASSESSMENT","verified_against_source requires a support assessment.",f"{path}.evidence[{i}].support_relation")
            if status=="corroborated" and len(set(refs)) < 2: result.add("error","CORROBORATED_WITH_FEWER_THAN_TWO_SOURCES","corroborated requires at least two distinct sources.",f"{path}.evidence[{i}].source_ids")
            if status=="unknown" and refs: result.add("warning","UNKNOWN_WITH_SOURCE","Unknown claim has source references; clarify the unresolved relation.",f"{path}.evidence[{i}]")
        basis=criterion.get("evidence_basis",{}); btype=basis.get("type"); refs=basis.get("source_ids",[]) or []
        if btype in {"empirical_evidence","stakeholder_input"} and not refs: result.add("error","BASIS_WITHOUT_SOURCE",f"{btype} requires source_ids.",f"{path}.evidence_basis")
        if btype=="no_evidence" and criterion.get("judgment_code") not in {"unknown","not_applicable"}: result.add("error","DEFINITE_JUDGMENT_WITH_NO_EVIDENCE","no_evidence cannot support a definite judgment.",f"{path}.judgment_code")

    for i,a in enumerate(items_at(record,"evidence","artifacts")):
        ref=a.get("reference",""); verification=a.get("verification",{}); integ=get_path(verification,"integrity","status")
        if ref=="#":
            if a.get("satisfies_requirements"):
                result.add("error","INLINE_ARTIFACT_INELIGIBLE_FOR_CAPABILITIES","Inline self-references cannot satisfy formal artifact capabilities.",f"evidence.artifacts[{i}].satisfies_requirements")
            if integ=="verified": result.add("error","INLINE_ARTIFACT_CANNOT_BE_HASH_VERIFIED","Inline self-reference cannot be integrity verified.",f"evidence.artifacts[{i}].verification.integrity")
        elif ref.startswith("file:"):
            path,error=_safe_local_path(ref)
            if error: result.add("error","UNSAFE_LOCAL_ARTIFACT",error,f"evidence.artifacts[{i}].reference"); continue
            assert path is not None
            if not path.exists() or not path.is_file(): result.add("error","LOCAL_ARTIFACT_MISSING",f"Missing file: {path}",f"evidence.artifacts[{i}].reference"); continue
            try:
                if path.stat().st_size>MAX_LOCAL_ARTIFACT_BYTES: result.add("error","LOCAL_ARTIFACT_TOO_LARGE",f"Artifact exceeds {MAX_LOCAL_ARTIFACT_BYTES} bytes.",f"evidence.artifacts[{i}].reference"); continue
            except OSError as exc: result.add("error","LOCAL_ARTIFACT_STAT_FAILED",str(exc),f"evidence.artifacts[{i}].reference"); continue
            if path.suffix.lower() not in ALLOWED_LOCAL_ARTIFACT_SUFFIXES: result.add("error","LOCAL_ARTIFACT_EXTENSION_NOT_ALLOWED",f"Unsupported extension: {path.suffix}",f"evidence.artifacts[{i}].reference")
            if integ=="verified":
                expected=get_path(verification,"integrity","sha256")
                actual=hashlib.sha256(path.read_bytes()).hexdigest()
                if not expected or expected.lower()!=actual.lower(): result.add("error","ARTIFACT_HASH_MISMATCH",f"SHA-256 mismatch for {a.get('artifact_id')}.",f"evidence.artifacts[{i}].verification.integrity.sha256")
        else:
            parsed=urlparse(ref)
            if parsed.scheme in {"http","https"}:
                if integ=="verified": result.add("error","REMOTE_ARTIFACT_NOT_LOCALLY_VERIFIED","Remote references cannot be marked integrity verified without a local snapshot.",f"evidence.artifacts[{i}].verification.integrity.status")
            else: result.add("warning","OPAQUE_ARTIFACT_REFERENCE","Artifact reference is neither file:, #, nor HTTP(S).",f"evidence.artifacts[{i}].reference")
        structural=get_path(verification,"structural_completeness","status")
        if structural=="passed" and integ!="verified": result.add("error","STRUCTURE_PASSED_WITHOUT_INTEGRITY","Structural completeness requires verified integrity.",f"evidence.artifacts[{i}].verification")
        method=get_path(verification,"methodological_review","status")
        reviewer=get_path(verification,"methodological_review","reviewer",default={})
        if method=="approved" and get_path(reviewer,"type") not in {"human_methodologist","authorized_panel"}: result.add("error","INVALID_METHODOLOGICAL_APPROVER","Methodological approval requires a qualified human reviewer.",f"evidence.artifacts[{i}].verification.methodological_review.reviewer")
        if method=="approved" and not get_path(verification,"methodological_review","reviewed_at"): result.add("error","METHODOLOGICAL_APPROVAL_MISSING_DATE","Methodological approval requires reviewed_at.",f"evidence.artifacts[{i}].verification.methodological_review.reviewed_at")
    return result

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("record",type=Path); a=p.parse_args()
    try:return print_result(validate(load_record(a.record)))
    except Exception as exc: print(f"ERROR EXECUTION: {exc}"); return 2
if __name__=="__main__": raise SystemExit(main())
