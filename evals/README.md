# Agent evals

`evals/evals.json` defines realistic output-quality tasks and assertions, including narrative category repair, experience planning, term pragmatics, learning transfer, and explicit brevity controls. `evals/trigger_queries.json` classifies requests as `narrative_support`, `canonical_record`, or `formal_grade_precheck` and records expected profile and pack selection. `evals/profile-and-pack-cases.json` adds profile, pack, overapplication, underapplication, and metamorphic cases. `evals/decision-formation-cases.json` adds pre-EtD alternative-quality, epistemic-role, minimal-property, natural-language correction, Reverse Projection, Formation Update, and proportionality cases for the local Decision Formation layer.

In Formation cases, `formation_expected` describes visible or material Formation
(Question exploration, alternative formation, or EtD handoff). A `false` case
may still retain the internal minimal `tree_mermaid` diagnostic, provided it is
not exposed and does not trigger additional I/O or a Formation ritual.

Run each output eval in a clean context at least three times per comparison mode:

1. with the skill path supplied;
2. without the skill as a baseline.

Store outputs, output form, profile, pack, timing, and assertion grading in an external workspace. The bundled unit tests validate definitions only; they do not imply that live agent runs occurred.

Recommended workspace shape:

```text
workspace/iteration-1/<eval-id>/with_skill/{outputs,timing.json,grading.json}
workspace/iteration-1/<eval-id>/without_skill/{outputs,timing.json,grading.json}
```
