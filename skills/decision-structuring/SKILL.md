---
name: decision-structuring
description: "Structure, inspect, and revise supplied decision material as Context, Questions, Alternatives, and a generated Mermaid Tree. Use when options are missing, incoherent, incomparable, or need explanation, or when supplied corrections change the decision structure. Return material information gaps to the caller."
---

# Decision Structuring

Turn supplied material into a small, explainable decision structure. Read the
[property model](references/formation-properties.md) for its definitions and
the [workflow](references/workflow.md) to form, check, or revise a case.

## Scope and inputs

Start from the supplied request, case material, interpretation, candidate
options, or existing formation state. Inputs may be incomplete. Structure and
check what is available; return material missing-information needs with their
decision relevance. The caller owns request interpretation, research, user
interviews, appraisal criteria, final advice, and presentation policy.

Write `context.description` first, then `context.sensemaking`, then `objects`.
Sensemaking records the supplied interpretation, not independently invented
user goals. Keep missing interpretation explicit. Preserve facts, explicit
negations, unknowns, and hypotheses when updating either narrative field.

## Form and revise

1. Organize Context and form the smallest useful Questions. Each Question has
   only `premise`, `splitter`, and `actions`; unresolved actions stay empty.
2. Generate the Mermaid Tree from semantic state and form coherent, comparable
   Alternatives with only local `label` and `description` properties.
3. Run Reverse Projection: every material alternative feature must be explained
   by Context or Questions, and each split must make a meaningful difference.
4. Apply supplied corrections to Context or Questions, then regenerate both
   projections. Report unresolved gaps and material changes to the caller.

Zero or one provisional alternative is valid; actual comparison requires at
least two coherent alternatives. Do not invent a choice for a factual request
or a workflow step to fill a Question's actions. Retain a minimal internal Tree
for each structuring pass; the caller chooses when to expose it.

## Model applicability

During use, check whether the definitions preserve the distinctions needed by
the case. Separate missing case information from a limitation of the model.
Competency questions describe model requirements; formation Questions describe
the current decision. Do not turn competency questions into case facts.

For substantial assessment or revision of the model itself, consult the
`conceptual-modeling` skill. The caller provides that skill when needed and
owns adoption of any revised definition. If it is unavailable, report the
modeling need rather than silently rewriting this contract. Ordinary case
structuring uses the existing definitions without changing shared model files.

## Result

Return the structured state or requested view, together with material gaps and
the effects of revisions. These can be ordinary prose; no separate mandatory
envelope or persistent IDs are required. External appraisal findings are
supplied case material, not a dependency on any particular appraisal method.
