# Decision Structuring Workflow

## Source of truth and projections

The principal source of truth is the pair **Formation Context + Questions**:

Questions are the primary meaning unit: preserve a material distinction here
before projecting it into a Tree or alternative description.

- `context.description` describes the domain situation;
- `context.sensemaking` follows it and records the user-oriented interpretation;
- `context.objects` is an extensible set of case material, each with a unique
  local string `label` and otherwise free-form payload;
- each Question has only `premise`, `splitter`, and `actions`;
- `actions: []` records a material but unresolved splitter and must not be
  filled with invented actions.

`context.sensemaking` is a user-oriented narrative input. It explains the request,
purpose, framing, premise repairs, latent agency, and practical meaning; it is
not external evidence and does not replace user values. `alternatives` and
`tree_mermaid` are generated projections of Context and Questions. They can be
revised in response to user language, but not by treating a diagram node or
alternative label as an independent ID or source of truth.

Before projection, promote any material fact, constraint, or distinction found
in `context.sensemaking` into `context.description`, a labelled
`context.objects` entry, or a Question, retaining its evidential status. Narrative prose may explain a
choice, but it must not become an untracked branch.

The Tree is a view of the semantic state, not an independent source of truth.
The internal representation is the `tree_mermaid` string. Mermaid aliases are
ephemeral render details, not stable identifiers. Do not add a parallel Tree
schema, Question IDs, alternative references, or a second assumption registry
to make the diagram easier to manipulate.

## Prepare supplied material

First write `context.description` from the supplied domain situation, then
record the supplied interpretation in `context.sensemaking`. Preserve the
original request and the distinction between facts, negations, unknowns, and
hypotheses. If an interpretation is not supplied, keep that gap explicit rather
than inventing user motivations. Present Context as `description`, `sensemaking`,
then `objects`; revisit both narrative fields against the source when revising.

Use labelled `context.objects` for case material without imposing a fixed
facts, constraints, evidence, or source schema. Distinguish user statements,
research findings, and reference-model coverage prompts by their meaning and
provenance. A model's suggested criterion is not a fact or a user preference.
Identify missing information and why it could change a distinction or option;
return those needs to the caller rather than conducting research or interviews.

## Form Questions

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

## Project the Tree

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

## Form Alternatives

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
comparison, require at least two coherent and comparable
alternatives. If that condition is not met, return to Context or Questions;
having two labels alone is not sufficient.

## Reverse Projection

For each material feature of each alternative, identify the Question or Context
element that explains it. Check both directions:

1. **Alternative to Formation:** an unexplained difference is a hidden
   assumption, missing Question, missing fact, or missing constraint; update the
   semantic source and re-project.
2. **Formation to Alternative:** a Question that creates no material difference
   may be merged, removed, or retained as an explicit unresolved distinction
   when its relevance is not yet known.

Also check abstraction mismatch, internal contradiction, infeasible or
dominated straw-men, duplicated options, unrepresented case-realistic option
families, and technically reachable but incoherent combinations. Reverse
Projection is the guard against hidden assumptions and fake diversity before comparison.

## Update from supplied feedback

The user corrects formation in ordinary language. Interpret “that split is
wrong,” “this branch is missing,” or “these options are the same” as a semantic
revision to Context and/or Questions, then regenerate the Mermaid Tree and
alternatives. Do not accept direct edits to Mermaid nodes, aliases, or option
labels as a separate mutation path. Return one targeted clarification need to the caller when the correction is
materially ambiguous.

Route supplied feedback by semantic type:

- return to **Questions** for a new decision-sensitive distinction, switching
  condition, contestable assumption, option granularity defect, or abstraction
  mismatch;
- return to **Context** for a fact, hard or soft constraint, evidence gap,
  feasibility boundary, resource or legal condition, or implementation fact
  that does not itself define an option axis;
- update both when the finding genuinely contains both kinds of meaning.

The underlying fact or evidence remains in Context even when its threshold also
becomes a Question. Re-project and report any material change to the comparison.
The caller decides what further information gathering or appraisal is needed.

## Stop proportionately

Stop when another distinction is unlikely to change a coherent alternative,
its viability, or its comparability. Return unresolved material gaps explicitly.
Clear supplied alternatives need no artificial third option. A factual or
learning request need not become a decision between invented alternatives.

Use ordinary semantic operations: add, revise, merge, or remove a Question;
update Context; regenerate the Tree and alternatives. Do not standardize a large mutation language in this release.
Avoid independent Question levels, resolution states, or routing flags when
the meaning is already represented by the three Question properties and Context.
