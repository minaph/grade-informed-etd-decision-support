# GRADE Claim Rules

Read this file whenever GRADE-rated evidence or formal GRADE EtD labeling is assessed.

## Layer 1: GRADE evidence assessment

`requirements_met` requires:

- comparative health outcomes in the supported formal scope;
- critical or important desirable and undesirable outcomes;
- outcome-level certainty with all domains considered;
- a consistent initial-to-final calculation or explicit justified override in the form
  `override: domains=<certainty_domain[,certainty_domain]>; rationale=<case-specific reason>`;
- artifacts covering search, selection, risk of bias, synthesis, certainty domains, outcome certainty, and Evidence Profile or SoF;
- integrity and structural checks;
- methodological approval by a `human_methodologist` or `authorized_panel`.

## Layer 2: GRADE EtD precheck

`precheck_passed` requires:

- a formal GRADE EtD draft profile in the supported scope;
- a passed evidence structural precheck;
- explicit criterion judgments and recommendation semantics;
- an evidence basis for each applicable criterion;
- no unexplained definite judgment where evidence is absent.

A precheck does not authorize a public formal claim.

## Layer 3: formal authorization

`authorized` requires an imported, `human_approved` record.

- Evidence-certainty authorization requires a human methodologist or authorized panel.
- Recommendation or decision authorization requires an authorized panel.
- Generated records cannot be authorized.

## Artifact capabilities

One artifact may satisfy several requirements. Integrity and structural checks may be automated; methodological approval cannot be supplied by AI or an automated validator.

`calculation_or_override` is bounded to 4,096 characters so validation remains
available under adversarial or accidentally oversized inputs.
