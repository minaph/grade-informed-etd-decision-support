# Migration

## Decision-structuring extraction

Use `skills/decision-structuring/SKILL.md` for the reusable formation model and
workflow. Its references are relative to its own directory. The old
`references/formation-properties.md` redirects to that contract, and
`references/question-formation.md` now contains parent orchestration only.
Callers supply the case and interpretation, resolve returned information needs,
and decide how to appraise or present the results. No criterion mapping to
Generic EtD is required. Question and Alternative properties are unchanged.

## Context interpretation placement

Move any existing top-level `sensemaking` string to `context.sensemaking`,
immediately after `context.description` and before `context.objects` in the
formation view. Preserve its content and epistemic status; do not retain a
second top-level copy. For new drafting, write the domain description first,
then the interpretation, and check both against the original material.
This local Formation change does not alter Canonical Schema 3.1.0.

## Formation contract 0.6.0 to 0.7.0

This change does not alter Canonical Schema 3.1.0 and therefore requires no
Canonical Record migration. If an external workflow used the previous internal
Formation notes, translate them to the new property model:

- keep user-oriented interpretation in the free-form `context.sensemaking` string;
- put domain material in `context.description` or labelled `context.objects`
  (only the local string `label` is required);
- express each material splitter as one Question with only `premise`,
  `splitter`, and `actions`; use `actions: []` when unresolved;
- express provisional or formed alternatives as local `label` plus
  `description`; require two coherent, comparable alternatives only when
  comparison or EtD begins;
- regenerate the internal `tree_mermaid` string after semantic changes rather
  than preserving node or option IDs.
- treat Research and Interview as peer choices, but queue material Interview
  prompts while independent Research and relevant Preset review are completed;
  batch the prompts unless a material Question dependency requires a targeted
  early Interview.

The previous shallow Formation Context, Question Tree views, and assumption
lists are not persistence requirements. Do not add them to Canonical Schema.

## Schema 3.0.0 to 3.1.0

Valid Schema 3.0.0 records remain supported and do not need immediate migration.

If a Schema 3.0 record selects a legacy Domain Pack that does not define
`scope.included_use_cases` and a complete assessment for every current candidate,
prefer leaving the record on Schema 3.0. To migrate it, choose one explicit path:

- detach the legacy Pack by setting `domain_packs_considered: []`,
  `candidate_assessments: []`, `domain_pack_ids: []`, and
  `domain_pack_use_case: null`; or
- replace it with a current `academic` or `software_engineering` Pack, select one
  included use case, and record a selected-or-excluded assessment for every Pack
  candidate.

Do not copy a selected legacy Pack unchanged into a Schema 3.1 record.

For a new or migrated Schema 3.1.0 record:

1. change `schema_version` to `3.1.0`;
2. add a registry-backed top-level `profile_id`;
3. add `adaptation.domain_pack_ids`, matching selected `domain_packs_considered` entries in order;
4. add `adaptation.domain_pack_use_case`: use one value from the selected pack's `scope.included_use_cases`, or `null` when no pack is selected;
5. select at most one Domain Pack;
6. optionally replace non-applicable full criterion objects with compact applicability and reason objects;
7. run `validate_profiles.py` and `validate_all.py`.

Do not assign an official `grade.*` profile by inference when question family, perspective, or conclusion form is unknown. Use `generic.etd` and record the limitation.

## Schema 2.x to 3.0.0

1. Set `schema_version: 3.0.0`.
2. Replace `formal_grade` with `formal_grade_etd_draft` where applicable.
3. Remove `grade_claim_allowed`, `grade_claim_reason`, and `grade_claim_assessment`.
4. Add `grade_evidence_assessment`, `grade_etd_assessment`, `formal_grade_claim_authorization`, and `etd_framework`.
5. Replace focal/comparator fields with `contrasts` and `active_contrast_id`.
6. Add `contrast_id` to every effect estimate and certainty assessment.
7. Add outcome role, type, and population-importance rationale.
8. Replace certainty `rating` with initial and final ratings, domain effects, and calculation or override.
9. Separate artifact integrity, structural completeness, and methodological review.
10. Add explicit criterion evidence bases and language-neutral machine codes.
11. Add Domain Pack version, SHA-256, candidate assessments, and composition notes.
12. Leave template `created_at` null and set it only when generating a case record.
