# Decision Formation Property Model

This document is the property contract for the local Decision Formation layer.
It deliberately describes a small semantic object rather than a second
Canonical EtD schema. The contract applies to internal formation state and to
the narrative-side view of a case; it does not change Canonical Schema 3.1.0.

## Design goals

- Keep the meaning that an AI can explain in long natural-language strings.
- Keep the pieces that drive comparison small enough to inspect and revise.
- Derive diagrams and alternatives from semantic state instead of maintaining
  several independently editable representations.
- Allow the case to add information without forcing a fixed ontology for every
  domain or evidence source.

## Working object

The conceptual working object has these top-level properties:

```yaml
sensemaking: "A user-oriented account of what the request means, why it matters, and where its framing may be incomplete."
context:
  description: "Domain context in which the decision or request sits."
  objects:
    - label: "deployment constraint"
      detail: "The first release must run in the existing region."
questions:
  - premise: "The organization must introduce the capability without losing operational control."
    splitter: "Can the capability be introduced in stages while control is retained?"
    actions:
      - "Introduce it in one controlled stage"
      - "Introduce it incrementally by workflow"
alternatives:
  - label: "Staged internal rollout"
    description: "Start with a controlled workflow and expand after operational evidence is available."
  - label: "Incremental workflow rollout"
    description: "Introduce the capability one workflow at a time and use each result to guide the next."
tree_mermaid: |
  flowchart TD
    root["Control must be retained"] --> q1{"Staged introduction?"}
    q1 -->|"one controlled stage"| a1["Staged internal rollout"]
    q1 -->|"incremental by workflow"| a2["Incremental workflow rollout"]
```

## Whole-system model

The property relationships and feedback routes are:

```mermaid
flowchart LR
  R["raw request"] --> S["sensemaking\nuser-oriented narrative"]
  S --> C["context\ndescription + labelled objects"]
  C --> Q["questions\npremise / splitter / actions"]
  S --> Q
  Q --> T["tree_mermaid\ngenerated internal projection"]
  Q --> A["alternatives\nlabel + description"]
  X["Research\ncase-specific reality"] -.->|"facts / constraints"| C
  I["Interview\nuser-specific values"] -.->|"goals / tradeoffs"| C
  P["Preset reference model\ncoverage prompt"] -.->|"omission / framing prompt"| Q
  C -->|"domain grounding"| T
  C -->|"case rationale"| A
  A -->|"attach when semantically explained"| T
  A --> RP["reverse projection\nmaterial mapping check"]
  T --> RP
  RP -->|"unexplained difference"| C
  RP -->|"missing or redundant splitter"| Q
  A --> E["EtD appraisal\nonly after coherent comparison"]
  E -->|"fact / constraint / evidence gap"| C
  E -->|"switching condition / option defect"| Q
  U["user natural-language correction"] --> C
  U --> Q
```

The arrows describe semantic dependencies, not a requirement to expose every
stage in every answer. `tree_mermaid` and `alternatives` are regenerated after a
material Context or Question update; EtD is rerun only when that regeneration
changes the comparison materially. The dotted inputs preserve the epistemic
roles described below: Research contributes case reality, Interview contributes
user-specific values, and a preset contributes coverage prompts rather than
evidence, authority, or mandatory fields.

### Selection versus scheduling

Research and Interview are peer candidates when selecting which uncertainty to
resolve. Choose between them by epistemic role and expected materiality rather
than by a universal Research-first rule. Research addresses case reality;
Interview addresses user-specific values and private constraints.

After selecting the material information needs, schedule user involvement
separately. Queue Interview prompts instead of scattering interruptions through
the formation pass. If useful formation work can proceed without those answers,
complete the relevant Research and Preset review loop first and then ask the
queued Interview questions as one coherent batch. This reduces repeated user
attention and avoids questions that the research or coverage check may make
unnecessary.

An Interview may start earlier when a material later Question depends on its
answer and no independent Research, Preset review, Context work, or Question
work remains. Ask only the smallest targeted Interview needed to unblock that
dependency. This is an interaction-scheduling rule, not a ranking of Research
over Interview.

The object is conceptual: do not copy it into the Canonical Record. A case may
start with only `sensemaking`, `context`, and an empty `questions` or
`alternatives` list. Properties may be absent from a provisional internal
snapshot when they are not yet needed, but a delivered formation view should
make unresolved materiality explicit rather than silently filling gaps.

### `sensemaking`

`sensemaking` is a free-form string written for the user. It explains the
literal request, purpose, premise repairs, framing tensions, latent decision or
agency, and the practical meaning of the case. It is intentionally not a
controlled list or a short status code. It is an interpretive input to
formation, not external-world evidence and not a substitute for user values.

### `context`

`context.description` is a free-form string for domain context. Keep it
distinct from `sensemaking`: the former describes the case world; the latter
explains the user's request and its interpretation.

Every member of `context.objects` is a mapping with only a unique local string
`label` as its required property:

```yaml
label: "a unique local name"
```

The `label` must be a non-empty string unique within this Formation. All other
properties are optional and unconstrained by this skill. They may carry a fact,
constraint, EtD finding, research result, preset prompt, interview response,
or any domain-specific payload that the current case needs. Do not introduce a
fixed `source`, `role`, `type`, or nested facts/constraints schema merely to
make objects look uniform. When provenance matters, explain it in the object's
free-form payload or in the surrounding narrative while preserving the
epistemic boundaries in `question-formation.md`.

`objects` is therefore an extensible case surface, not a hidden canonical
ontology. An empty array is valid.

### `questions`

Each Question mapping has exactly these three properties and no additional
formation fields:

```yaml
premise: "The situation in which this Question matters."
splitter: "The distinction that divides that premise into materially different paths."
actions: ["A candidate design or decision move", "Another candidate move"]
```

- `premise` and `splitter` are strings and may be long enough to preserve the
  reasoning needed to interpret them.
- `actions` is an array of strings. Each item is a candidate design or
  decision move, not a workflow step or an instruction to the user.
- `actions: []` is valid and means that the Question is currently unresolved.
  Never invent actions to make an unresolved Question appear complete. If the
  Question is material, use Research or selective Interview, or ask the user
  for the missing decision; otherwise carry it as an explicit uncertainty.
- Do not add Question IDs, level fields, resolution states, challenge modes,
  routing flags, or action objects in this release.
- One Question describes one material splitter. If there are independent
  splitters, create separate Questions rather than hiding several axes in one
  object.

Questions, together with `context`, are the authoritative formation semantics.
Before projecting, promote any material fact, constraint, or distinction found
in `sensemaking` into Context or a Question; explanatory prose alone must not
silently drive an alternative. Question count is not a quality score; keep only
distinctions that can change a strong alternative, its design principle, its
viability, or comparability.

### `alternatives`

Each alternative mapping has exactly these two properties and no additional
formation fields:

```yaml
label: "Staged internal rollout"
description: "A coherent design principle and enough implementation meaning to compare it."
```

The `label` is a unique local display name within the current Formation. It is
not a stable machine ID and must not be used as an implicit cross-record
reference. The `description` is a free-form explanation at the same level of
abstraction as peer alternatives.

During exploration, zero or one provisional alternative is valid. Before a
comparison or EtD appraisal is attempted, there must be at least two coherent,
comparable alternatives. Two labels alone are insufficient: if the alternatives
are duplicates, caricatures, or abstraction mismatches, return to Questions or
Context and re-form them. Do not add a status quo, compromise, or maximal option
unless it is independently rational for the case.

Alternatives do not contain Question or action references. Their connection to
the option space is reconstructed semantically from descriptions, Question
premises, splitters, and actions.

### `tree_mermaid`

`tree_mermaid` is a string containing a Mermaid diagram generated from
`context`, `questions`, and the current alternatives. It is the internal Tree
representation for this release. Mermaid aliases are ephemeral render aliases;
they are not Question IDs, alternative IDs, or persistence keys.

Question actions form the Tree skeleton. For `actions: []`, render the Question
as an unresolved node with no invented outgoing branch. Attach an alternative at the action
leaf or in an annotation when its design logic can be explained by that path.
If a material alternative or action cannot be mapped, annotate it as an
**unexplained alternative/action** and return to Context or Questions. Never
invent a semantic connection just to make the diagram look complete.

Generate and retain an internal `tree_mermaid` for every request, including a
daily or tightly specified request. For a direct request, keep the sketch minimal and
make it invisible in the answer. Show the Tree when
the topic is even moderately complex, deep, research-dependent, contains
multiple material branches, or when the user asks to inspect the structure.
Do not expose it when an answer-only, command-only, fixed-format, or similarly
narrow response makes the diagram distracting.

## Correction and regeneration contract

The user corrects the formation in ordinary language. Interpret a report such
as “that split is wrong,” “this branch is missing,” or “these two options are
the same” as a request to revise `context` and/or `questions` (and the
provisional narrative when needed), then regenerate `tree_mermaid` and `alternatives`.
The user does not edit Mermaid nodes directly, and Mermaid
aliases must not become a second source of truth. If the correction is
materially ambiguous, ask one targeted question rather than guessing a branch.

EtD feedback follows the same contract: switching conditions and option
definition defects revise Questions; facts, constraints, evidence gaps, and
feasibility findings revise Context. A finding can update both when it genuinely
contains both kinds of meaning. Re-project before rerunning EtD, and rerun only
if the regenerated comparison materially changes.
