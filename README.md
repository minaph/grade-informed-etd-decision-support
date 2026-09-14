# grade-informed-etd-decision-support

Version 0.7.0 applies GRADE Evidence-to-Decision principles through two output forms:

- `narrative_support` for ordinary answers and artifacts, with proportional and natural-language decision support;
- `canonical_record` for auditable, machine-readable decisions and optional formal GRADE prechecks.

The skill does not treat every request as a full EtD record. It separates the requested deliverable from the amount of visible decision scaffolding needed.

## Decision Formation

Version 0.7.0 retains the local Decision Formation layer while replacing its
over-specified state model with a small property contract. `context` and
`questions` are the semantic source of truth; `sensemaking` remains a flexible
user-oriented narrative, and `alternatives` plus `tree_mermaid` are generated
projections. The exact properties are documented in
`references/formation-properties.md`.

Narrative Sensemaking, case-specific Research, user Interview, preset reference models such as Domain Packs, and EtD appraisal retain distinct epistemic roles. Research establishes case reality; presets critique coverage; Interview resolves user-specific judgments when material; EtD evaluates formed alternatives and can feed back switching conditions or option-definition defects. Research and Interview are selected as peer epistemic options, but material Interview prompts are normally queued while independent Research and relevant Preset review are completed, then handled in a coherent batch; a dependency may justify a targeted early Interview. The Question Tree and alternatives are derived views rather than independent mutable stores.

This layer is a local GRADE-informed extension, not an official GRADE EtD component. Canonical Schema remains 3.1.0 in this release, and Formation state is not embedded into the Canonical Record. An internal Mermaid diagnostic is generated for every request to catch omissions, but it remains invisible for direct or tightly specified requests. Show it for moderately complex, deep, research-dependent, or explicitly structural requests; do not force Research, Interview, or a visible Formation ritual.

### Formation properties

The internal object has the following deliberately small shape:

```yaml
sensemaking: "free-form user-oriented narrative"
context:
  description: "free-form domain context"
  objects:
    - label: "unique local name"
      # any case-appropriate payload is allowed
questions:
  - premise: "where the question matters"
    splitter: "one material distinction"
    actions: ["candidate design or decision move"]
alternatives:
  - label: "unique local display name"
    description: "coherent comparable option"
tree_mermaid: "generated Mermaid string"
```

`actions: []` is an unresolved Question, not a cue to invent a branch. During
exploration there may be zero or one provisional alternative; comparison or EtD
requires at least two coherent, comparable alternatives. Users correct the
semantic state in ordinary language, after which the Tree and alternatives are
re-generated. Labels are local names rather than stable IDs, and no fixed
`source`/`role` schema is imposed on Context objects.

## Conceptual modeling dependency

Conceptual modeling is maintained independently at
`https://github.com/minaph/conceptual-modeling` and pinned as a Git submodule at
`skills/conceptual-modeling`. Its `SKILL.md` is the entry point; its interview
guide is separate from its integrated applicability, definition, and revision
guide. The child does not require Formation, EtD, or the parent's presets.

The parent manages model routing and the CQ-to-Question relationship in
`references/preset-routing.md`. CQs belong to model expression requirements;
Questions belong to the current situation and task. Routing checks semantic
coverage, the backing definition, and case information separately. This change
does not revise existing preset contents or their schemas.

After cloning the parent, initialize its pinned dependency:

```bash
git submodule update --init --recursive
```

A recursive Git clone is also supported. A source ZIP or a plain `git archive`
of the parent is not a complete installation; use a Git checkout with the
submodule initialized. Installing the child alone means placing that complete
repository in the host's skill search path or explicitly supplying its
`SKILL.md`. Submodule storage does not itself register a standalone skill.

For development, keep the independent checkout and the parent's pinned checkout
distinct. Commit and publish a reviewed child revision first, fetch it into the
submodule, check out that specific commit, then stage the gitlink and run parent
validation before committing the parent update. Do not substitute a separately
installed child version or use `git submodule update --remote` for normal use.

The parent manifest excludes the submodule's contents and Git metadata. The
package validator checks the indexed gitlink, initialized checkout, commit
match, clean child tree, child frontmatter, and local document references.
It also runs the `skills-ref` package CLI (`skills-ref` or `agentskills`) for
both skills when available. Run
`python scripts/update_manifest.py` after changing parent files. Validation
requires Git metadata and the initialized submodule; stage an intentional child
version update with `git add skills/conceptual-modeling` before validating it.

The former `references/model-design.md` and the revised guide have been replaced
by the independent skill and the parent's routing document. Their pre-extraction
versions remain in commit `58ecb5d` for comparison.

## Narrative upscaling

For short factual, event, terminology, comparison, and learning requests, `narrative_support` now runs a materiality-gated latent decision and agency pass. It preserves the literal answer, then checks whether premise repair, alternative framing, actual use or reception, historical development, lived experience, or user-controllable variables would change understanding or action.

When they do, the response adds only the high-yield dimensions and connects them to a low-regret default, meaningful variants, tradeoffs, switching conditions, or a learning action. Explicit brevity constraints and marginal-usefulness stop rules prevent encyclopedic expansion or visible EtD scaffolding.

## Reference Profiles

`references/official-grade-profiles.yaml` records the public GRADEpro defaults for:

- clinical recommendations from individual and population perspectives;
- coverage decisions;
- health-system and public-health recommendations and decisions;
- test recommendations from individual and population perspectives;
- test coverage decisions.

`generic.etd` is a local extension for non-GRADE work. Public GRADEpro documentation permits organisations to modify templates, so the registry records sourced defaults rather than claiming immutable minimum requirements.

## Domain Packs

The initial non-health packs are:

- `academic`: research priority and resource allocation, plan quality and feasibility, and output or method sharing;
- `software_engineering`: architecture and major technology selection, change strategy, secure development, and quality-attribute tradeoffs.

Each pack distinguishes public external sources from local mappings. Pack use is not certification, formal GRADE use, ethics approval, security assurance, or external endorsement. New Schema 3.1 records select at most one pack.

## Canonical Record compatibility

New records use Schema 3.1.0 with:

- `profile_id`;
- `adaptation.domain_pack_ids`;
- `adaptation.domain_pack_use_case`, set to an included use case of the selected pack or `null` when no pack is selected;
- compact entries for `not_applicable`, `outside_mandate`, and `integrated_elsewhere` criteria;
- profile-aware and pack-aware validation.

Valid Schema 3.0.0 records remain accepted. Canonical Records retain one active contrast. Non-formal records may leave recommendation direction and strength null when those controlled GRADE semantics do not fit.

Legacy Schema 3.0 Domain Packs are not automatically upgraded: keep the record
on 3.0, detach the old Pack selection, or replace it with a current Pack and
assess every current candidate. See `MIGRATION.md`.

## Formal GRADE boundaries

The skill keeps separate:

1. GRADE evidence-certainty assessment;
2. a structural GRADE EtD precheck;
3. formal claim authorization by a qualified human workflow.

A generated record cannot authorize itself. The implemented formal module remains limited to comparative health-intervention recommendations. Test profiles are registered for reference selection, but the linked-evidence diagnostic workflow is not implemented.

## Validation

```bash
python -m pip install -r requirements.txt
python scripts/validate_profiles.py --registry-only
python scripts/validate_all.py assets/canonical-etd-template.yaml
python -m unittest discover -s tests -p 'test_*.py'
python scripts/validate_evals.py
python scripts/validate_skill_package.py --require-skills-ref
```

Validator success proves structural consistency, not methodological correctness, official GRADE compliance, or decision authority.
