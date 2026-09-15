# Narrative Upscaling

## Purpose and relationship to the report model

Narrative Upscaling is a separate rule for deciding whether and how to enrich
an answer beyond its literal minimum. It selects background, explanatory
perspectives, examples, experience accounts, or learning support that help
fulfil the user's purpose.

The [Generic EtD model](models/generic-etd-model.md) defines evaluation, evidence and
uncertainty, recommendation, and the content needed to justify a report's
position. Use that model when evaluating and reporting a position or action.
Narrative Upscaling determines which supplementary material would help the
reader understand or use the answer, and how far that expansion should go.
An expansion may improve understanding even when it does not change the
recommendation. These rules do not add evaluation criteria or require a
separate report format.

## Decide whether to expand

Start with the requested deliverable and infer the decision structure behind
the request. Use stated purposes and hypothesize unstated action goals, values,
and alternatives. Carry plausible interpretations into reasoning and targeted
research; do not wait for the user to state a decision explicitly. Keep these
hypotheses distinct from confirmed intentions and revise them with new material
or user corrections. Consider
an addition when it would resolve a misleading premise, explain a material
variation, prevent a likely misunderstanding, or help the user apply or learn
what was requested. Identify that contribution before adding the material.
A short prompt warrants interpreting latent purposes, but its length alone
does not justify adding material without a useful contribution.

Consider differences between formal definitions and actual use, alternative
explanatory perspectives, historical development, experience across settings,
and variables the user can influence. Select the dimensions that serve this
request; do not apply all of them as a checklist.

Preserve the literal answer or requested artifact. Respect explicit brevity,
answer-only, command-only, and fixed-format constraints. Repair a false premise
without silently substituting a different question. For a terse event query,
preserve plausible intentions such as attending versus selling until the
available material or a targeted clarification distinguishes them.

## Select additions for the topic

### Organizations and categories

Clarify the relationship being asked about before introducing nearby categories.
Distinguish membership, association, historical relationships, and functional
similarity when conflating them would mislead the reader. Add a contrasting
perspective only if it changes how the subject is understood. Do not manufacture
multiple lenses to satisfy a count.

### Events and experiences

Select details according to the intended activity, such as visiting or selling.
Access, conditions, crowding, images, and dated experience accounts can clarify
what participation involves. Connect them to useful preparation or choices
when stated or inferred purposes make that help useful. Distinguish reported past experiences
from expectations for the current event; do not turn a brief query into a full
itinerary by default.

### Terms and concepts

Begin with the distinction needed to understand or use the terms. Add examples,
usage settings, register, or reception when they illuminate that distinction.
Include history or etymology only when it explains the contrast; it must not
substitute for evidence of present-day meaning. A recognition or production
question is useful when learning or practice is intended, not mandatory for
every terminology answer.

### Learning

Use stated prior knowledge as a bridge and infer plausible learning goals when
they are unstated. Choose among a contrast with familiar
concepts, a minimal working example, a short sequence, practice, feedback, and
a transfer task according to the learner's goal and requested depth. Explain
how to check an exercise when one is included. Pacing or difficulty can be
made adjustable where that helps the learner. Return a requested command or
fix without imposing a curriculum.

### Artifacts and actions

Deliver the requested artifact or action. Add explanations, usage examples,
variants, or failure conditions when they change how the result can be
understood or used. An implementation plan or continuing learning programme
belongs to the requested task when explicitly needed; it is not a requirement
of the generic report model or of every expansion.

## Connect interpretation to decision structuring

First prepare `context.description` from the supplied situation, then the
interpretation for `context.sensemaking`, including hypothesized goals, values,
and alternative intentions that can guide research and Questions. Follow
[the parent formation workflow](question-formation.md) when options or
explanatory positions need structuring. Decision Structuring owns Questions,
Alternatives, and the Tree. Narrative Upscaling can identify a missing
perspective or distinction, but passes that material back for structuring
rather than editing projections. Use the generic model for any resulting
comparison and recommendation, without repeating its evaluation rules here.

## Gather material by the information need

Research addresses case reality; Interview addresses user-specific values and
private constraints. Follow the scheduling rules in `question-formation.md`.
For time-sensitive facts across domains, such as prices, product specifications,
or service availability, verify current primary sources and retain the dates
needed to establish which conditions the evidence describes.

- For organizational relations, check the named relationship and distinguish
  formal membership from related, historical, or functional relationships.
- For events, verify current identity, date, venue, and constraints when needed.
  Use dated reports or images when they help establish experience differences;
  preserve their date and context instead of treating an old edition as current.
- For term usage, use dictionaries, corpora, or other usage sources when available
  to check claims about frequency, register, collocations, or reception.
  Identify illustrative linguistic judgment when usage evidence is unavailable.
- For learning, use the stated prior knowledge and available goals. Return a
  material missing goal or constraint through the parent interview workflow.

Do not infer private information such as the user's current location. Use it
only when supplied or authorized. Report source conflicts and missing evidence
rather than filling them with assumed facts.

## Stop expanding

Stop when the literal request is satisfied and another addition would not
resolve a relevant misunderstanding, explain a consequential difference, or
help the user apply or learn the answer. Remove repeated, weakly supported,
invasive, or tangential additions. Prefer one example with a clear purpose to
several examples that repeat the same point.

Stop gathering when further information would not support a useful addition
or resolve a material uncertainty within the requested scope. Missing evidence
may limit an expansion; it is not a reason to invent detail. Do not expose a
criteria table, a Tree, or other framework scaffolding merely because this
rule was used. Apply the caller's separate Tree-visibility policy when a
structuring view is requested or otherwise warranted.
