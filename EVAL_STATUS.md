# Evaluation status

Package version 0.7.0 introduces the Formation property contract and internal
Mermaid diagnostic. The structural checks below have been updated for that
contract. A clean-context live with/without-skill comparison of the revised
Formation cases was completed with `gpt-5.6-luna` (high reasoning).

## Generic EtD consolidation

The evaluation and report definition reside in
`references/generic-etd-model.md`. Answer enrichment, topic-specific additions,
and stopping remain separate rules in `references/narrative-upscaling.md`,
alongside interpretation and information gathering. Narrative eval
expectations have been aligned with purpose-dependent reporting; fixed counts
of lenses, images, variants, and exercises are no longer universal pass criteria.
The historical results below apply to their earlier prompts and rules, not to
this revised model. No new live model comparison is claimed for this change.

## Decision-structuring extraction validation

The local `skills/decision-structuring` extraction separates the reusable model
and workflow from parent research, interview, and appraisal orchestration.
Package checks cover both pinned submodule checkouts, subskill metadata,
local document links, and the YAML example contract. The earlier model experiments below predate this extraction;
they do not establish the behavior of the extracted skill. No new live
with/without-skill experiment is claimed for this change.

## Completed in this package

- JSON Schema meta-validation
- Unit, invariant, referential-integrity, governance, and security tests
- Representative-case validation
- Failure-case detection
- Hand-authored record-level metamorphic comparison
- Eval-definition, output-form, profile, pack, and metamorphic-case validation
- Local artifact root confinement, size, extension, existence, and SHA-256 checks
- Separation tests for GRADE evidence assessment, GRADE EtD precheck, and formal human authorization
- Narrative-upscaling definition checks for premise repair, events and experience, term pragmatics, prior-knowledge learning, and explicit brevity controls
- Decision Formation definition checks for polarized alternatives, Research versus preset epistemic roles, assumption relaxation, Reverse Projection, EtD feedback routing, and proportionality controls
- Formation property checks for the minimal Question and Context shapes, empty-action unresolved Questions, alternative comparison cardinality, Mermaid projection, and natural-language correction/reprojection
- Formation information-gathering scheduling checks for peer Research/Interview selection, queued Interview prompts, independent Research/Preset work, and dependency-triggered early Interview
- Clean-context live execution of all 13 Decision Formation cases in `evals/decision-formation-cases.json`: one with-skill and one without-skill run per case (26 runs total) using `gpt-5.6-luna` with high reasoning. Strict saved-response grading produced 53/53 assertion passes with the skill and 37/53 without it. The result is qualitative/structural evidence; execution timing and total-token metadata were not captured by the subagent notification channel.
- Four exploratory clean-context with-skill rounds across four draft iterations for user-derived short prompts, one run per selected prompt per iteration; findings strengthened full-pattern defaults and confirmed term, event, learning, answer-only, and command-only behavior.
- Final changed-feature comparison in an external workspace: six narrative cases × three repetitions × with/without skill (`final-v0.5.0`), followed by an 18-run with-skill rerun with the same 18 baseline runs reused (`final-v0.5.0-r2`). The first run showed 12/18 with-skill passes; after rule and evidence-grounding fixes, the rerun showed 15/18 with-skill passes. The remaining term case failure was the absence of a small recognition or production test.
- A final textual rule was added after `final-v0.5.0-r2` to require that small test unless brevity or answer-only constraints apply. That historical wording was not rerun as a model experiment; the current model supersedes it with purpose-dependent use of exercises.
- `skills-ref` 0.1.5 validation of the installed bytes through a temporary public-name alias was executed during the resumed verification; direct validation of the reconciled `skill-*` path rejects only the directory-name/frontmatter-name mismatch. The package validator now creates the same temporary alias when needed.

## Defined but not executed here

- Further clean-context live Agent repetitions beyond the completed final comparison and rerun
- Further with-skill versus without-skill comparisons beyond the completed final comparison
- Repeated output-form and profile/pack selection measurement
- Prompt-driven metamorphic runs
- Tool-trace, latency, and token collection
- Old-version versus new-version comparison
- Train/validation prompt split

## External human gates not completed

- Real GRADE methodologist review of real evidence products
- Authorized panel review of recommendation wording and scope
- Domain-expert and affected-stakeholder evaluation

The included formal artifacts are test fixtures for state transitions. They are not real systematic reviews, GRADE Evidence Profiles, or endorsements. Passing validators demonstrates structural consistency only.

Release CI must still run `validate_skill_package.py --require-skills-ref`; the validator now supplies a temporary public-name alias when the installed directory has a reconciled `skill-*` name. The consolidated report model should not be described as experimentally confirmed by the historical runs.
