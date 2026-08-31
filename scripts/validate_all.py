from __future__ import annotations
import argparse
from pathlib import Path
from validation_lib import ValidationResult,load_record,print_result
from validate_schema import validate as validate_schema
from validate_sources import validate as validate_sources
from validate_recommendation import validate as validate_recommendation
from validate_governance import validate as validate_governance
from validate_profiles import validate as validate_profiles
VALIDATORS=(validate_schema,validate_sources,validate_recommendation,validate_governance,validate_profiles)
def validate(record:dict)->ValidationResult:
    out=ValidationResult()
    for fn in VALIDATORS: out.extend(fn(record))
    return out
def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("record",type=Path); a=p.parse_args()
    try:return print_result(validate(load_record(a.record)))
    except Exception as exc: print(f"ERROR EXECUTION: {exc}"); return 2
if __name__=="__main__": raise SystemExit(main())
