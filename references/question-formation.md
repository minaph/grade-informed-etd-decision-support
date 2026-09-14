# Decision Formation and Question Formation

## Purpose and status

Use Decision Formation when the option space itself can change the quality of
the answer or EtD comparison: alternatives may be missing, underspecified,
artificially binary, extreme, straw-man-like, at mismatched abstraction levels,
or likely to omit a materially different option family.

This is a local GRADE-informed extension. It is not a new component of official
GRADE EtD and it must not weaken GRADE certainty, EtD precheck, or formal
human-authorization boundaries.

The property contract is in `references/formation-properties.md`. Read it when
maintaining the internal formation object. The objective is a small set of
coherent, realistic, comparable alternatives, not a large tree or an exhaustive
enumeration of options.

## Source of truth and projections

The principal source of truth is the pair **Formation Context + Questions**:

Questions are the primary meaning unit: preserve a material distinction here
before projecting it into a Tree or alternative description.

- `context.description` describes the domain situation;
- `context.objects` is an extensible set of case material, each with a unique
  local string `label` and otherwise free-form payload;
- each Question has only `premise`, `splitter`, and `actions`;
- `actions: []` records a material but unresolved splitter and must not be
  filled with invented actions.

`sensemaking` is a user-oriented narrative input. It explains the request,
purpose, framing, premise repairs, latent agency, and practical meaning; it is
not external evidence and does not replace user values. `alternatives` and
`tree_mermaid` are generated projections of Context and Questions. They can be
revised in response to user language, but not by treating a diagram node or
alternative label as an independent ID or source of truth.

Before projection, promote any material fact, constraint, or distinction found
in `sensemaking` into Context or a Question. Narrative prose may explain a
choice, but it must not become an untracked branch.

The Tree is a view of the semantic state, not an independent source of truth.
The internal representation is the `tree_mermaid` string. Mermaid aliases are
ephemeral render details, not stable identifiers. Do not add a parallel Tree
schema, Question IDs, alternative references, or a second assumption registry
to make the diagram easier to manipulate.

## Epistemic roles

Keep the following roles distinct even when they interact:

| Input or process | Epistemic role | It may contribute | It must not be treated as |
| --- | --- | --- | --- |
| Narrative Sensemaking | Interpret the request, purpose, premise, latent agency, and framing | `sensemaking`, candidate Questions, purpose tensions | external-world evidence or a substitute for user values |
| Research | Discover case-specific reality | Context objects, facts, constraints, existing option patterns, technical possibilities, evidence gaps | the user's preferences or a universal domain ontology |
| Interview | Resolve user-specific matters the AI cannot responsibly proxy | goals, priorities, acceptable tradeoffs, non-public constraints, value judgments | external evidence or a required ritual for every case |
| Preset reference model | Critique coverage and reduce arbitrary framing | prompts for Questions, missing criteria or option families | case-specific reality, authority, or a mandatory checklist |
| EtD appraisal | Compare formed alternatives and expose decision-sensitive feedback | switching conditions, evidence gaps, uncertainties, option-definition defects | a Question resolver, Tree router, or direct mutator of projections |

Research and preset models can disagree without either being automatically
privileged. Route the disagreement to Context or Questions according to the
kind of claim at issue.

能力質問（CQ）はモデル定義の表現要件に属し、意思決定の問い（Questions）は現在の状況と作業目的に属します。
モデルを選ぶ際は、`references/preset-routing.md` に沿って、能力質問と定義が重要な区別を表現できるか確認します。
一つの意思決定の問いを複数の能力質問が支えることもあり、事例固有の価値や制約は別途確認します。

候補モデルから重要な論点が見つかった場合は、状況の記述（Context）または意思決定の問いへ反映してから、
分岐図と選択肢を再生成します。能力質問は、判断に関係するものを選んで使います。
能力質問との対応は補足の文章に記録し、形成用の記録には既存の形式を用います。

概念モデリングスキルは、単独で利用できる汎用的な作業手順を提供します。
親スキルは、その成果を状況の記述と意思決定の問いへ反映し、聞き取りの時期を次節の規則に沿って調整します。

### Selection versus scheduling

Treat Research and Interview as peer candidates when deciding which uncertainty
to address. Choose between them by epistemic role and expected materiality, not
by a universal Research-first rule. Research addresses case reality; Interview
addresses user-specific values and private constraints.

Once candidate information needs are known, schedule them separately from that
selection. Queue material Interview prompts instead of scattering user
interruptions through the formation pass. When useful work can proceed without
those answers, complete the currently relevant Research and Preset review loop
first, then ask the queued Interview questions as one coherent batch. This
reduces repeated user attention and also avoids asking questions that the case
research or coverage check may make unnecessary.

Do not defer an Interview merely for batching when a material later Question
depends on its answer and no independent Research, Preset review, Context work,
or Question work remains. In that exception, ask the smallest targeted
Interview needed to unblock the dependency, then continue the queue when it is
efficient to do so. This is an interaction-scheduling rule, not an epistemic
ranking of Research over Interview.

## Formation workflow

### 0. Internal diagnostic Tree

Generate and retain an internal `tree_mermaid` for every request, including a
daily request or a request whose alternatives are already clear. This internal
sketch is a check for a broken split, an omitted material branch, or an
unimportant Question; it does not imply that visible Formation, Research,
Interview, or EtD is required.

For a direct command or tightly specified answer, keep the sketch minimal and
do not mention it. Show the Tree when the case is even moderately complex,
deep, research-dependent, has multiple material branches, or when the user asks
to inspect the structure. An answer-only, command-only, fixed-format, or
similarly narrow request keeps the Tree internal.

### 1. PREPARE

Start from the raw request. Write a user-facing `sensemaking` narrative and a
domain-facing Context. Repair a false premise without silently replacing the
request. Identify whether each material uncertainty calls for Research,
Interview, a preset coverage check, or more formation work; do not assume a
fixed tool order. Add Research only when case reality could materially alter
the option space. Consult a preset reference model only when it can reveal a
plausible omission or arbitrary framing. Use selective Interview only when a
user value or private constraint materially changes the choice, applying the
scheduling rule above to batch user involvement when possible.

Do not build a deep hierarchy before these semantic materials are adequate. Do
not split Context into fixed facts, constraints, evidence, or source arrays;
put the needed material in labelled `context.objects` with a case-appropriate
payload.

### 2. FORM QUESTIONS

Form the smallest useful set of Questions. A Question asks what would have to
differ for another rational alternative to exist. Its `premise` states where it
matters, its `splitter` states one material distinction, and its `actions` list
candidate design or decision moves. Actions are not workflow instructions.

Prioritize a Question when plausible answers would change a strong alternative,
introduce or eliminate an option family, change a material design principle,
change viability, or expose that candidate options are not comparable. Keep
unresolved Questions with `actions: []`; do not ask the user every Question or
convert uncontested facts into Questions. Independent splitters are separate
Questions rather than hidden axes in one object.

### 3. PROJECT THE TREE

Render Context and Questions as the Mermaid `tree_mermaid` string. Question
actions form the Tree skeleton; later Questions are connected only when an
earlier answer changes which later distinction is meaningful. Normal explanatory
nodes are optional and should not duplicate semantic claims.

Attach an alternative at an action leaf or annotation when its design logic can
be explained by that path. If a material alternative or action cannot be
explained by the current Context and Questions, mark it as an **unexplained
alternative/action** and return to formation. Never invent a branch solely to
make the diagram look complete.

Do not maintain separate Expanded and Simplified trees. When an audit needs
more or less detail, derive a view or excerpt from the same semantic state and
Mermaid projection. The concise view must not silently delete a material
distinction.

### 4. FORM ALTERNATIVES

Treat reachable paths as candidate answer bundles, not as an instruction to
enumerate every combinatorial path. Form alternatives with unique local display
`label`s and free-form `description`s. Do not add Question or action references;
the semantic mapping is checked during Tree rendering and Reverse Projection.

A strong alternative is internally coherent, feasible enough to evaluate, at a
comparable abstraction level, a rational design principle rather than a
caricature, and materially different from its peers. Cosmetic wording changes
are not diversity. A status quo, compromise, or maximal option is included only
when independently rational for the case.

Zero or one provisional alternative is valid while exploring. Before a direct
comparison or EtD appraisal, require at least two coherent and comparable
alternatives. If that condition is not met, return to Context or Questions;
having two labels alone is not sufficient.

### 5. REVERSE PROJECTION

For each material feature of each alternative, identify the Question or Context
element that explains it. Check both directions:

1. **Alternative to Formation:** an unexplained difference is a hidden
   assumption, missing Question, missing fact, or missing constraint; update the
   semantic source and re-project.
2. **Formation to Alternative:** a Question that creates no material difference
   may be collapsed, demoted, or retained only as a reassessment trigger.

Also check abstraction mismatch, internal contradiction, infeasible or
dominated straw-men, duplicated options, unrepresented case-realistic option
families, and technically reachable but incoherent combinations. Reverse
Projection is the guard against hidden assumptions and fake diversity before
EtD.

## Hand off to EtD appraisal

Once the alternatives pass Reverse Projection and the two-or-more comparison
gate, evaluate them with the existing proportional GRADE-informed EtD process.
Decision Formation does not alter criteria, evidence rules, Domain Pack rules,
formal-claim boundaries, or Canonical Record validation. A Domain Pack remains
a preset reference model, never case evidence or authority.

For `narrative_support`, compare multiple formed alternatives in ordinary
language. For `canonical_record`, retain one active contrast; form alternatives
first, create the necessary contrast-specific records, and synthesize
transparently. Never embed the Question Tree or internal property object into
Canonical Schema 3.1.0.

## Formation Update from user or EtD feedback

The user corrects formation in ordinary language. Interpret “that split is
wrong,” “this branch is missing,” or “these options are the same” as a semantic
revision to Context and/or Questions, then regenerate the Mermaid Tree and
alternatives. Do not accept direct edits to Mermaid nodes, aliases, or option
labels as a separate mutation path. Ask one targeted question only when the
correction is materially ambiguous.

After appraisal, route feedback by semantic type:

- return to **Questions** for a new decision-sensitive distinction, switching
  condition, contestable assumption, option granularity defect, or abstraction
  mismatch;
- return to **Context** for a fact, hard or soft constraint, evidence gap,
  feasibility boundary, resource or legal condition, or implementation fact
  that does not itself define an option axis;
- update both when the finding genuinely contains both kinds of meaning.

The underlying fact or evidence remains in Context even when its threshold also
becomes a Question. Re-project before rerunning EtD, and rerun only when the
regenerated comparison, operative conditions, or recommendation materially
changes. EtD is therefore a feedback generator for Formation, not a route
destination that resolves Questions.

## Proportional stopping and operations

Do not attempt exhaustive option-space search. Stop visible Formation when
another Question, Research step, Interview, or EtD iteration is unlikely to
change a strong alternative or recommendation, is low-materiality, costs more
than its expected decision value, or can be learned through a reversible or
staged action. Continue when a plausible missing family, hidden assumption,
hard constraint, or switching condition could reverse the choice or materially
alter implementation.

Clear, low-stakes, answer-only, command-only, or tightly specified requests
retain their internal diagnostic Tree but should not expose a Formation ritual
or request unnecessary I/O. Ready alternatives should be compared directly;
do not invent a third option merely to satisfy a count.

Use ordinary semantic operations: add, revise, merge, or remove a Question;
update a Context object; project or re-project the Tree; form or re-form
alternatives; request Research or Interview; or apply EtD feedback. Do not standardize a large mutation language in this release. In particular, avoid
independent Question levels, resolution states, challenge modes, routing flags,
or branch-relaxation commands when the same meaning can be represented by the
three Question properties, Context, and projection state.

## Persistence boundary

In version 0.7.0, Decision Formation remains internal or narrative-side.
Canonical Schema remains 3.1.0, and `tree_mermaid`, Questions, alternatives,
and reverse-projection history are not persisted in the Canonical Record. Add a
separate provenance structure only after repeated audited workflows show that
long-lived formation history cannot be reconstructed from the semantic case
materials.
