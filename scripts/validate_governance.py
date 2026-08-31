from __future__ import annotations
import argparse
import re
import unicodedata
from collections import Counter
from pathlib import Path
from validation_lib import *

RATING_ORDER={"very_low":0,"low":1,"moderate":2,"high":3}
EFFECT_POINTS={"downgrade_2":-2,"downgrade_1":-1,"no_change":0,"upgrade_1":1,"upgrade_2":2,"not_applicable":0}
OVERRIDE_PLACEHOLDER_FRAGMENTS={
    "justification goes here", "lorem ipsum", "review required",
    "placeholder", "not specified", "see above", "to be determined",
}

def _override_is_justified(value:object)->bool:
    text=str(value or "").strip()
    match=re.fullmatch(
        r"override:\s*domains=([a-z_, ]+);\s*rationale=(.+)",
        text,
        flags=re.IGNORECASE,
    )
    if not match:
        return False
    domains={item.strip().lower() for item in match.group(1).split(",") if item.strip()}
    reason=" ".join(match.group(2).split())
    lowered=unicodedata.normalize("NFKC", reason).casefold()
    alphanumeric=[character for character in lowered if character.isalnum()]
    frequencies=Counter(alphanumeric)
    unique_characters=set(frequencies)
    unique_bigrams=set(zip(alphanumeric, alphanumeric[1:]))
    dominant_ratio=(
        max(frequencies.values()) / len(alphanumeric)
        if alphanumeric else 1.0
    )
    return (
        bool(domains)
        and domains.issubset(CERTAINTY_DOMAINS)
        and len(reason)>=50
        and len(alphanumeric)>=30
        and len(unique_characters)>=12
        and len(unique_bigrams)>=20
        and dominant_ratio<=0.30
        and not any(fragment in lowered for fragment in OVERRIDE_PLACEHOLDER_FRAGMENTS)
    )

def _certainty_consistency(result:ValidationResult, record:dict)->None:
    for i,item in enumerate(items_at(record,"evidence","certainty_of_effects")):
        initial=item.get("initial_rating"); final=item.get("final_rating"); domains=item.get("domains",{})
        if initial=="not_rated" or final=="not_rated":
            if initial!=final: result.add("error","PARTIAL_NOT_RATED_CERTAINTY","Initial and final ratings must both be not_rated.",f"evidence.certainty_of_effects[{i}]")
            continue
        effects=[]; unclear=False
        for key in CERTAINTY_DOMAINS:
            eff=get_path(domains,key,"rating_effect")
            if eff=="unclear": unclear=True
            elif eff in EFFECT_POINTS: effects.append(EFFECT_POINTS[eff])
        if unclear: result.add("error","UNCLEAR_CERTAINTY_DOMAIN","Formal calculation cannot contain unclear domains.",f"evidence.certainty_of_effects[{i}].domains")
        if initial in RATING_ORDER and final in RATING_ORDER:
            expected=max(0,min(3,RATING_ORDER[initial]+sum(effects)))
            override=item.get("calculation_or_override","")
            override_justified=_override_is_justified(override)
            if str(override).strip().lower().startswith("override:") and not override_justified:
                result.add("error","CERTAINTY_OVERRIDE_JUSTIFICATION_MISSING","Override must use 'override: domains=<certainty_domain>; rationale=<substantive case-specific reason>' with valid affected domains and a non-placeholder rationale.",f"evidence.certainty_of_effects[{i}].calculation_or_override")
            if RATING_ORDER[final]!=expected and not override_justified:
                result.add("error","CERTAINTY_CALCULATION_MISMATCH",f"Expected rating index {expected} from documented domain effects, got {final}.",f"evidence.certainty_of_effects[{i}].final_rating")

def _formal_criterion_basis(result:ValidationResult, record:dict)->None:
    for name,criterion,path in iter_criteria(record):
        if criterion.get("applicability",{}).get("status")!="applicable": continue
        basis=criterion.get("evidence_basis",{}); btype=basis.get("type"); refs=basis.get("source_ids",[]) or []
        if btype in {"empirical_evidence","stakeholder_input"} and not refs: result.add("error","FORMAL_APPLICABLE_CRITERION_WITHOUT_SOURCE",f"{name} has no source for its evidence basis.",f"{path}.evidence_basis")
        if btype=="no_evidence" and (criterion.get("support")!="insufficient" or criterion.get("judgment_code") not in {"unknown","not_applicable"}): result.add("error","FORMAL_NO_EVIDENCE_OVERSTATED",f"{name} with no evidence must remain insufficient and unknown.",path)
        if btype=="panel_judgment" and not str(basis.get("rationale","")).strip(): result.add("error","FORMAL_PANEL_JUDGMENT_WITHOUT_RATIONALE",f"{name} panel judgment needs rationale.",f"{path}.evidence_basis.rationale")

def validate(record:dict)->ValidationResult:
    result=ValidationResult(); g=record.get("governance",{}); origin=g.get("record_origin"); review=g.get("review_status"); profile=g.get("methodological_profile")
    auth=g.get("formal_grade_claim_authorization",{}); auth_status=auth.get("status"); auth_scope=auth.get("scope"); auth_by=auth.get("authorized_by") or {}
    if origin=="generated_by_skill":
        if review!="draft": result.add("error","GENERATED_RECORD_NOT_DRAFT","Generated records must remain draft.","governance.review_status")
        if auth_status=="authorized": result.add("error","AI_GENERATED_RECORD_CANNOT_AUTHORIZE_FORMAL_CLAIM","Generated records cannot carry formal authorization.","governance.formal_grade_claim_authorization.status")
        if g.get("approved_by") is not None or g.get("approved_at") is not None: result.add("error","DRAFT_HAS_APPROVAL_METADATA","Generated drafts cannot have approval metadata.","governance")
    if origin=="imported_approved_record" and review=="human_approved":
        if not g.get("approved_by") or not g.get("approved_at") or not g.get("approval_scope"): result.add("error","APPROVED_IMPORT_MISSING_METADATA","Approved imports need complete approval metadata.","governance")
    if review=="human_approved" and origin!="imported_approved_record": result.add("error","HUMAN_APPROVED_ORIGIN_INVALID","Only imported approved records may be human_approved.","governance")

    formal=profile=="formal_grade_etd_draft"
    if formal and g.get("human_review_required") is not True: result.add("error","FORMAL_GRADE_REQUIRES_HUMAN_REVIEW","Formal GRADE profile always requires human review.","governance.human_review_required")
    if formal:
        dtype=get_path(record,"decision_case","question","decision_type"); qtype=get_path(record,"decision_case","question","evidence_question_type")
        if dtype not in FORMAL_GRADE_DECISION_TYPES or qtype!=FORMAL_GRADE_EVIDENCE_QUESTION_TYPE: result.add("error","FORMAL_GRADE_SCOPE_UNSUPPORTED","Formal profile is currently limited to comparative health-intervention recommendations.","decision_case.question")

    _certainty_consistency(result,record)
    outcomes={x.get("outcome_id"):x for x in items_at(record,"decision_case","question","outcomes")}
    qtype=get_path(record,"decision_case","question","evidence_question_type")
    for i,item in enumerate(items_at(record,"evidence","certainty_of_effects")):
        outcome=outcomes.get(item.get("outcome_id"),{})
        if item.get("final_rating")!="not_rated" and (outcome.get("outcome_type")!="health" or qtype!=FORMAL_GRADE_EVIDENCE_QUESTION_TYPE): result.add("error","GRADE_RATING_OUTSIDE_SUPPORTED_HEALTH_EVIDENCE","GRADE ratings are only allowed for supported comparative health outcomes.",f"evidence.certainty_of_effects[{i}].final_rating")

    evidence_assessment=g.get("grade_evidence_assessment",{}); etd_assessment=g.get("grade_etd_assessment",{})
    evidence_refs=set(evidence_assessment.get("artifact_refs",[]) or [])
    etd_refs=set(etd_assessment.get("artifact_refs",[]) or [])
    caps_structural=artifact_capabilities(record,False,evidence_refs)
    caps_method=artifact_capabilities(record,True,evidence_refs)
    evidence_missing_struct=REQUIRED_GRADE_EVIDENCE_CAPABILITIES-caps_structural
    evidence_missing_method=REQUIRED_GRADE_EVIDENCE_CAPABILITIES-caps_method
    active=get_path(record,"decision_case","question","active_contrast_id")
    required_health=outcome_ids(record,important_only=True,health_only=True)
    rated={(x.get("contrast_id"),x.get("outcome_id")) for x in items_at(record,"evidence","certainty_of_effects") if x.get("final_rating") in RATING_ORDER}
    unrated=sorted(o for o in required_health if (active,o) not in rated)
    roles={x.get("role") for x in items_at(record,"decision_case","question","outcomes") if x.get("importance") in {"critical","important"} and x.get("outcome_type")=="health"}
    if evidence_assessment.get("automated_precheck")=="passed":
        if not evidence_refs: result.add("error","GRADE_EVIDENCE_PRECHECK_WITHOUT_ARTIFACT_REFS","Passed evidence precheck requires artifact references.","governance.grade_evidence_assessment.artifact_refs")
        if evidence_missing_struct: result.add("error","GRADE_EVIDENCE_PRECHECK_MISSING_CAPABILITIES",f"Missing structural capabilities: {sorted(evidence_missing_struct)}","governance.grade_evidence_assessment")
        if unrated: result.add("error","GRADE_EVIDENCE_PRECHECK_UNRATED_OUTCOMES",f"Unrated important health outcomes: {unrated}","evidence.certainty_of_effects")
        if not {"desirable","undesirable"}.issubset(roles): result.add("error","GRADE_EVIDENCE_PRECHECK_MISSING_OUTCOME_ROLES","Both desirable and undesirable important health outcomes are required.","decision_case.question.outcomes")
    if evidence_assessment.get("status")=="requirements_met":
        if evidence_assessment.get("automated_precheck")!="passed": result.add("error","GRADE_EVIDENCE_REQUIREMENTS_MET_WITHOUT_PRECHECK","requirements_met requires a passed precheck.","governance.grade_evidence_assessment")
        if evidence_missing_method: result.add("error","GRADE_EVIDENCE_REQUIREMENTS_MET_WITHOUT_METHOD_REVIEW",f"Capabilities lack methodological approval: {sorted(evidence_missing_method)}","evidence.artifacts")
        if unrated: result.add("error","GRADE_EVIDENCE_REQUIREMENTS_MET_WITH_UNRATED_OUTCOMES",f"Unrated outcomes: {unrated}","evidence.certainty_of_effects")

    if etd_assessment.get("status")=="precheck_passed":
        if not formal: result.add("error","ETD_PRECHECK_REQUIRES_FORMAL_PROFILE","EtD precheck requires formal_grade_etd_draft.","governance.methodological_profile")
        if evidence_assessment.get("automated_precheck")!="passed": result.add("error","ETD_PRECHECK_REQUIRES_GRADE_EVIDENCE_PRECHECK","EtD precheck requires a passed GRADE evidence structural precheck.","governance.grade_evidence_assessment.automated_precheck")
        if not etd_refs: result.add("error","GRADE_ETD_PRECHECK_WITHOUT_ARTIFACT_REFS","EtD precheck requires artifact references.","governance.grade_etd_assessment.artifact_refs")
        missing_etd=REQUIRED_GRADE_ETD_CAPABILITIES-artifact_capabilities(record,False,etd_refs)
        if missing_etd: result.add("error","GRADE_ETD_PRECHECK_MISSING_CAPABILITIES",f"Missing EtD capabilities: {sorted(missing_etd)}","evidence.artifacts")
        _formal_criterion_basis(result,record)
        if get_path(record,"conclusion","decision_status")=="recommendation_formed":
            if get_path(record,"conclusion","recommendation","direction") not in {"for","against"} or get_path(record,"conclusion","recommendation","strength") not in {"strong","conditional"}: result.add("error","GRADE_ETD_RECOMMENDATION_SEMANTICS","Formal EtD recommendation semantics are incomplete.","conclusion.recommendation")

    if auth_status=="authorized":
        if origin!="imported_approved_record" or review!="human_approved": result.add("error","FORMAL_AUTHORIZATION_REQUIRES_APPROVED_IMPORT","Authorization requires an imported human-approved record.","governance.formal_grade_claim_authorization")
        if auth_scope in {"evidence_certainty","both"} and evidence_assessment.get("status")!="requirements_met": result.add("error","EVIDENCE_AUTHORIZATION_WITHOUT_REQUIREMENTS","Evidence authorization requires requirements_met.","governance.grade_evidence_assessment.status")
        if auth_scope in {"recommendation_or_decision","both"}:
            if etd_assessment.get("status")!="precheck_passed": result.add("error","ETD_AUTHORIZATION_WITHOUT_PRECHECK","EtD authorization requires precheck_passed.","governance.grade_etd_assessment.status")
            if auth_by.get("type")!="authorized_panel": result.add("error","ETD_AUTHORIZATION_REQUIRES_PANEL","Recommendation/decision authorization requires an authorized panel.","governance.formal_grade_claim_authorization.authorized_by")
        elif auth_scope=="evidence_certainty" and auth_by.get("type") not in {"human_methodologist","authorized_panel"}: result.add("error","EVIDENCE_AUTHORIZATION_REQUIRES_METHOD_REVIEWER","Evidence authorization requires a human methodologist or authorized panel.","governance.formal_grade_claim_authorization.authorized_by")
        if not auth.get("authorized_at"): result.add("error","FORMAL_AUTHORIZATION_MISSING_DATE","Authorization needs authorized_at.","governance.formal_grade_claim_authorization.authorized_at")
    elif auth_scope!="none": result.add("error","UNAUTHORIZED_SCOPE_MUST_BE_NONE","Non-authorized status must use scope none.","governance.formal_grade_claim_authorization.scope")
    if origin == "generated_by_skill" and g.get("created_at") is None:
        result.add("warning","GENERATED_RECORD_MISSING_CREATED_AT","Set created_at at generation time.","governance.created_at")
    return result

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("record",type=Path); a=p.parse_args()
    try:return print_result(validate(load_record(a.record)))
    except Exception as exc: print(f"ERROR EXECUTION: {exc}"); return 2
if __name__=="__main__": raise SystemExit(main())
