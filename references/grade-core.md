# Core Methodological Position

## Scope

For ordinary generic EtD evaluation and reports, use
[Generic EtD model](generic-etd-model.md). This reference covers GRADE evidence,
formal claims, and Canonical Record compatibility. The report model owns its
criteria, recommendation principles, and reporting depth.

## Separate claims

The record distinguishes:

- whether GRADE requirements for evidence certainty are met;
- whether a GRADE EtD recommendation or decision passes structural prechecks;
- whether a qualified human workflow authorizes the formal public claim.

These states are not interchangeable.

## Implemented formal scope

The formal module in this version supports comparative health-intervention recommendations with patient-important desirable and undesirable outcomes.

The module does not implement the specialized evidence chains required for diagnostic tests, screening, prognosis, model-based HTA, network meta-analysis, or GRADE-CERQual.

## Evidence certainty

For a supported formal assessment, record an active contrast, critical or important health outcomes, initial certainty, explicit downgrade and upgrade domains, final certainty, calculation path, and an Evidence Profile or Summary of Findings capability.

GRADE-rated evidence may be used in a GRADE-informed decision process. This does not make the EtD process itself formal GRADE EtD.

## EtD profiles and criteria

Use the published GRADEpro template differences in `official-grade-profiles.yaml` as Reference Profiles. Treat them as sourced template defaults because GRADEpro permits organizations to modify templates.

Canonical Records retain the ten standard slots for compatibility. A non-applicable slot may contain only applicability and a reason. Additional criteria use the fixed extension array.

The diagnostic/test profiles are registered for accurate reference selection, but the current formal module does not implement their linked-evidence chain.
