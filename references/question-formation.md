# Parent Integration of Decision Structuring

Use [decision-structuring](../skills/decision-structuring/SKILL.md) to structure,
check, and revise supplied material. Its property model and workflow own the
Context-Question-Alternative-Tree contract, formation steps, Reverse Projection,
and semantic correction rules. Do not redefine those contracts here.

The parent owns request interpretation, research, interviews, reference-model
selection, appraisal, and presentation. It supplies material and consumes the
subskill's structured state and missing-information needs. Generic EtD remains
an external consumer and feedback source; no EtD-specific fields or criterion
mapping are required by the subskill.

## Epistemic roles

Keep the following roles distinct even when they interact:

| Input or process | Epistemic role | It may contribute | It must not be treated as |
| --- | --- | --- | --- |
| Narrative Sensemaking | Interpret the request, purpose, premise, latent agency, and framing | `context.sensemaking`, candidate Questions, purpose tensions | external-world evidence or a substitute for user values |
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

## Invoke the subskill

For every parent request, invoke the subskill for a minimal internal diagnostic.
Keep it invisible for narrow outputs; show the Tree for moderately complex,
deep, research-dependent, or explicitly structural requests. This invocation
policy belongs to the parent and does not require external information gathering.

Prepare the domain situation first, then the user-oriented interpretation for
`context.sensemaking`, preserving explicit negations, unknowns, and hypotheses.
Supply these together with available findings and corrections. When option
formation is material, run the subskill's Question formation, Tree projection,
Alternative formation, and Reverse Projection workflow.

Resolve material missing-information needs through Research, Interview, or
reference-model review according to their epistemic roles and the scheduling
rules above. Feed the resulting material back for revision; do not mutate a
Mermaid node or option label as an independent semantic store.

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

## Return appraisal feedback

Supply switching conditions and option-definition defects for Question revision;
supply facts, constraints, evidence gaps, and feasibility findings for Context
revision. One finding can affect both. The subskill regenerates projections and
reports whether the comparison changed. Rerun appraisal only when that change
materially affects the comparison, operative conditions, or recommendation.
EtD is therefore a feedback generator for Formation, not a Question resolver.

Stop further information gathering or appraisal when its expected decision
value is low. Preserve unresolved material gaps instead of implying completion.

## Persistence boundary

In version 0.7.0, Decision Formation remains internal or narrative-side.
Canonical Schema remains 3.1.0, and `tree_mermaid`, Questions, alternatives,
and reverse-projection history are not persisted in the Canonical Record. Add a
separate provenance structure only after repeated audited workflows show that
long-lived formation history cannot be reconstructed from the semantic case
materials.
