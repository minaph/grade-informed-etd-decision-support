from __future__ import annotations
import argparse
from pathlib import Path
from validation_lib import *

CANONICAL_DECISIVE=set(STANDARD_CRITERIA)

def _code(record:dict,criterion:str): return get_path(record,"criteria",criterion,"judgment_code")
def validate(record:dict)->ValidationResult:
    result=ValidationResult(); c=record.get("conclusion",{}); status=c.get("decision_status"); r=c.get("recommendation",{}) if isinstance(c.get("recommendation"),dict) else {}
    direction=r.get("direction"); strength=r.get("strength"); conditions=r.get("conditions",[]) or []
    formal=get_path(record,"governance","methodological_profile")=="formal_grade_etd_draft"
    legacy=record.get("schema_version")=="3.0.0"
    if status=="recommendation_formed":
        if (formal or legacy) and (direction not in {"for","against"} or strength not in {"strong","conditional"}): result.add("error","FORMAL_OR_LEGACY_RECOMMENDATION_INCOMPLETE","A formal GRADE or Schema 3.0 recommendation needs direction and strength.","conclusion.recommendation")
        if not formal and not legacy and (direction is None) != (strength is None): result.add("error","PARTIAL_RECOMMENDATION_SEMANTICS","Direction and strength must both be set or both be null.","conclusion.recommendation")
        if strength=="conditional" and not conditions: result.add("error","CONDITIONAL_WITHOUT_CONDITIONS","A conditional recommendation requires operative conditions.","conclusion.recommendation.conditions")
    elif status=="insufficient_basis":
        if direction is not None or strength is not None: result.add("error","INSUFFICIENT_BASIS_HAS_RECOMMENDATION","Direction and strength must be null.","conclusion.recommendation")
        if not c.get("unresolved_uncertainties"): result.add("error","INSUFFICIENT_WITHOUT_UNCERTAINTIES","Uncertainties are required.","conclusion.unresolved_uncertainties")
        if not c.get("next_actions"): result.add("error","INSUFFICIENT_WITHOUT_NEXT_ACTION","Next actions are required.","conclusion.next_actions")
    allowed=set(CANONICAL_DECISIVE)|{f"additional:{x.get('criterion_id')}" for x in items_at(record,"additional_criteria")}
    for i,name in enumerate(c.get("decisive_criteria",[]) or []):
        if name not in allowed: result.add("error","UNKNOWN_DECISIVE_CRITERION",f"Unknown decisive criterion: {name}",f"conclusion.decisive_criteria[{i}]")
    ratings={x.get("final_rating") for x in items_at(record,"evidence","certainty_of_effects")}
    if status=="recommendation_formed" and strength=="strong" and ratings.intersection({"low","very_low"}): result.add("warning","STRONG_WITH_LOW_CERTAINTY","Strong recommendation with low certainty requires exceptional justification.","conclusion.recommendation.strength")
    if status=="recommendation_formed" and strength=="strong" and ratings=={"not_rated"}: result.add("warning","STRONG_WITH_UNRATED_EFFECTS","Strong recommendation with unrated effects needs explicit justification and human review.","conclusion.recommendation.strength")
    harms=_code(record,"undesirable_effects"); equity=_code(record,"equity"); feas=_code(record,"feasibility"); acc=_code(record,"acceptability"); bal=_code(record,"balance_of_effects")
    if status=="recommendation_formed" and direction=="for":
        if harms=="effect_large" and strength=="strong": result.add("error","STRONG_FOR_WITH_LARGE_HARMS","Large harms conflict with an unexplained strong-for recommendation.","criteria.undesirable_effects.judgment_code")
        if equity in {"equity_probably_reduced","equity_reduced"} and not c.get("implementation_conditions"): result.add("error","NEGATIVE_EQUITY_WITHOUT_MITIGATION","Negative equity needs mitigation.","conclusion.implementation_conditions")
        if feas in {"feasibility_probably_no","feasibility_no"} and not conditions and not c.get("implementation_conditions"): result.add("error","LOW_FEASIBILITY_WITHOUT_CONDITIONS","Low feasibility requires conditions.","conclusion")
        if acc in {"acceptability_probably_no","acceptability_no"} and strength=="strong": result.add("warning","STRONG_FOR_LOW_ACCEPTABILITY","Low acceptability requires explicit justification.","criteria.acceptability.judgment_code")
        if bal in {"balance_favors_comparator","balance_probably_favors_comparator"}: result.add("error","FOR_CONTRADICTS_BALANCE","Recommendation contradicts the balance judgment.","criteria.balance_of_effects.judgment_code")
    if status=="recommendation_formed" and direction=="against" and bal in {"balance_favors_option","balance_probably_favors_option"}: result.add("error","AGAINST_CONTRADICTS_BALANCE","Recommendation contradicts the balance judgment.","criteria.balance_of_effects.judgment_code")
    return result

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("record",type=Path); a=p.parse_args()
    try:return print_result(validate(load_record(a.record)))
    except Exception as exc: print(f"ERROR EXECUTION: {exc}"); return 2
if __name__=="__main__": raise SystemExit(main())
