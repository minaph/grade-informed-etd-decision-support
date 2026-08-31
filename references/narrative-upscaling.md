# Narrative Upscaling Guide

## Purpose

Upscale `narrative_support` when a short request contains a useful latent decision, experience, or learning problem. Preserve the literal request and add only the context that can materially change what the user understands, chooses, prepares, or does.

Upscaling is not encyclopedic expansion. It is a search for consequential variation and user agency.

## Run the latent decision and agency pass

Answer these questions silently after identifying the requested deliverable:

- Would correcting a premise, category, or boundary change the answer?
- Would a different framing or summary lens produce a meaningfully different account?
- Do formal structure, actual use, social reception, or lived experience diverge?
- Is the user plausibly preparing, choosing, learning, creating, or acting, and can they control relevant variables?
- Is the answer time-sensitive or dependent on date, place, audience, skill level, or other context?

Upscale when at least one answer is yes, the addition can be supported, and it is proportionate to the request. Treat explicit requests for detail, review, comparison, a report, or EtD analysis as strong signals. Respect requests for an answer-only, command-only, fixed-format, or otherwise narrow response.

A named query family is a lens, not a mandatory checklist. Start with the
literal deliverable and select only the family dimensions whose omission could
change understanding or action. A short prompt can still contain a material
premise or framing problem, but brevity alone does not require every available
layer. An explicit brevity or exact-output constraint overrides expansion.

## Boundary with Decision Formation

Narrative Upscaling interprets the request; it does not own the option-space model. Store the interpretation as the free-form `sensemaking` string described in `references/formation-properties.md`. When the latent decision pass shows that the supplied alternatives are missing, coarse, extreme, straw-man-like, mismatched in abstraction, or likely to omit a materially different option family, hand that interpretation to `question-formation.md`.

Do not build a Question Tree inside Narrative Upscaling. The global Formation
diagnostic may still generate its internal `tree_mermaid` for the request, but
Narrative Upscaling does not own or edit that projection. Narrative Sensemaking
may suggest candidate Questions, but case-specific facts belong to Research,
user-specific value judgments belong to Interview when material, and coverage
prompts from Domain Packs or other preset models remain reference-model input.
Decision Formation decides whether those materials actually warrant new
Questions or alternatives.

## Build the minimum useful expansion

1. **Deliver the core.** Give the literal answer, artifact, or immediate explanation first.
2. **Repair without substitution.** If the premise or category appears wrong, state that directly, distinguish `not found` from `does not exist`, and introduce the nearest plausible interpretations without silently replacing the user's wording.
3. **Map consequential variation.** Select only the high-yield axes:
   - structure and taxonomy: formal rules, categories, membership, or internal relations;
   - semantics and framing: boundaries, interpretations, and how the chosen lens changes a summary;
   - pragmatics and reception: where, by whom, and with what register or connotation something is used or encountered;
   - history and temporality: origin, development, and current status;
   - experience and context: sequence, environment, logistics, and reported variation in outcomes;
   - agency: choices, preparation, practice, or other variables the user can change.
4. **Ground the expansion.** Prefer current primary sources for live facts. Use dated archival material for historical relations. Use several reports or images to identify experience variables, and label reported patterns, synthesis, and inference separately. Do not infer private context such as current location; use it only when provided or authorized.
5. **Make the variation actionable.** When a choice or action is present, give a robust default that works under ordinary assumptions, credible variants, their tradeoffs, and the conditions that should switch the user away from the default. A default is a low-regret starting point, not a universally correct answer.
6. **Return agency to the user.** End with a usable next action, diagnostic, exercise, or at most one targeted question when the missing answer would materially change the work.

## Apply query-family patterns

### Factual, organizational, or category questions

- Answer the named relation or category first.
- Check for a false premise or terminology mismatch.
- If a hierarchy or category boundary is material, distinguish formal internal
  structure from external, historical, or functional relations and say when a
  relation is not established in the checked sources.
- Choose the smallest mapping that prevents a lens shift from being mistaken
  for a fact. A neutral reusable wording is useful when the original category
  is ambiguous; do not manufacture a fixed table for a simple lookup.

### Events and experience-oriented requests

- Resolve a terse venue-plus-activity fragment enough to distinguish the likely
  intent (for example, attending versus selling) without silently discarding a
  plausible branch.
- Verify current identity, date, venue, and official constraints when they
  matter. If sources conflict, disclose the conflict; do not use an old edition
  as clean support for a current claim.
- Add access, weather, crowd conditions, images, dated reports, route sequence,
  or priority variants only when they would change the user's plan and the
  relevant tools or sources are available. If no origin is provided, do not
  imply a current-location route; give generic access or ask for an origin only
  when personalization is materially useful.

### Concepts, terms, and word differences

- Choose among present-day meaning, useful historical development, and
  contemporary pragmatic distribution according to what changes the user's
  understanding. Include all three only when each earns its space.
- Never use etymology as proof of current meaning, and omit historical detail that does not illuminate the contrast.
- For pragmatic distribution, compare common settings, collocations, register, connotation, and how speakers or readers are likely to receive the term.
- For claims about contemporary frequency, register, collocations, or likely speaker reaction, check at least one dictionary, corpus, or other usage source when retrieval is available. State which observations the source supports. If no usage check is available, label examples as illustrative linguistic judgment and avoid unverified frequency or `native speakers think` claims.
- Keep sourced usage evidence distinct from linguistic intuition. Add a small
  recognition or production test only when the user is learning or practicing,
  and leave an unanswered item with a way to check it.

### Learning requests

- Use the user's stated prior knowledge as the bridge rather than restarting from first principles.
- Contrast the familiar and new mental models, then move from a minimal working example to a short lesson sequence, practice, feedback, and a realistic transfer task.
- Surface the learner-controlled variables: pacing, exercise difficulty, feedback loop, and project choice.
- If the user asks only for a command or fix, supply it first and do not force a curriculum.

### Artifact and action requests

- Produce the requested artifact or action first.
- Add rationale, variants, failure modes, or implementation conditions only when they change safe or effective use.
- Do not turn a reversible, tightly specified task into an unsolicited policy analysis.

## Stop proportionately

Stop expanding when the core request is satisfied, the material variation and low-regret default are clear, and further detail would be repetitive, weakly supported, invasive, or unlikely to change understanding or action. Do not expose EtD headings, a criteria table, or a Canonical Record merely because this pass was used.
