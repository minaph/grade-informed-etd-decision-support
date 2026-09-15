# Changelog

## 0.9.0

- 親の目的を、概念モデリングを基礎とする日常生活・他分野への実務応用へ更新。
- `evidence-based-writing` を独立公開し、文章作成・推敲のサブスキルとして固定版を参照。
- `references/models/` と `models/etd/` を用途に応じて整理し、参照資料の README を追加。
- 三つのサブスキルを対象に依存先の検証を統一し、モデル適用と文章作成の評価定義を追加。

## 0.8.0

- Canonical Record と専用の保存・検証機構、正式 GRADE の自動事前検査、旧形式の互換性を廃止。
- 5分野のドメインパックを、対象単位・概念の区別・根拠と限界を示す自然言語の参照モデルへ再構成。
- 保存欄への対応、候補の全件評価、1パック制限を廃止し、複数分野の意味を照合する適用規則へ変更。
- 公式プロファイルを参照情報として維持し、入口・評価定義・開発時の検証を更新。

## 0.7.0

- Reworked Decision Formation around a small property contract in `references/formation-properties.md`.
- Kept `context` and `questions` as the semantic source of truth while making `sensemaking` and other explanatory strings free-form.
- Reduced Questions to `premise`, `splitter`, and `actions`; allowed `actions: []` for unresolved material questions and removed implicit Question/action IDs and state fields.
- Reduced Context to `description` plus extensible `objects` whose only required property is a unique local string `label`.
- Defined alternatives as unique local `label` plus `description`, with a two-or-more coherent/comparable gate only when comparison or EtD begins.
- Made the internal Question Tree a generated `tree_mermaid` string, generated for every request but shown only when complexity or user intent makes it useful; natural-language corrections update Context or Questions and re-project.
- Relaxed narrative query-family guidance from fixed full patterns to materiality-selected lenses while preserving source, privacy, and formal GRADE boundaries.
- Kept Research and Interview as peer epistemic choices while scheduling user-facing Interview prompts in a queue: complete independent Research and relevant Preset review first when possible, batch the prompts, and allow a targeted early Interview only for a material dependency.
- Left Canonical Schema at 3.1.0 and kept formation state non-persistent; added property, correction, and internal-diagnostic evaluation coverage.

## 0.6.0

- Added a local Decision Formation layer before EtD appraisal for missing, coarse, extreme, straw-man-like, abstraction-mismatched, or materially incomplete alternatives.
- Added `references/question-formation.md` with shallow Formation Context, Questions as the semantic core, Question Tree projection, Expanded/Simplified views, strong-alternative formation, Reverse Projection, EtD feedback, and proportional stopping.
- Separated the epistemic roles of Narrative Sensemaking, case-specific Research, user Interview, preset reference models, and EtD appraisal.
- Kept Question state and operation vocabulary intentionally minimal; Tree topology changes remain Tree-level operations and Research/Interview remain external I/O.
- Added Formation Update routing so switching conditions and option-definition defects can revise Questions while facts, constraints, and non-option-defining evidence gaps revise Formation Context.
- Added explicit boundaries from Narrative Upscaling and adaptation rules into Decision Formation without turning Domain Packs into case evidence or authority.
- Added Decision Formation eval definitions covering polarized alternatives, case-specific research, preset anti-omission, assumption relaxation, reverse projection, fake diversity, EtD switching-condition feedback, feedback routing, and proportionality controls.
- Left Canonical Schema at 3.1.0; Decision Formation remains an internal or narrative-side process pending repeated evidence that durable formation provenance is needed.
- Updated package version metadata and manifest for 0.6.0 while preserving existing GRADE evidence, EtD precheck, and formal authorization boundaries.

## 0.5.0

- Added a materiality-gated narrative upscaling guide for short factual, organizational, event, terminology, learning, artifact, and action requests.
- Added a latent decision and agency pass spanning premise repair, framing, semantics, pragmatics, history, experience, and user-controllable variables.
- Added low-regret defaults, credible variants, tradeoffs, switching conditions, and targeted next actions without requiring visible EtD scaffolding.
- Added primary-source, dated-report, image-synthesis, inference-labeling, and private-context boundaries for live and experience-oriented answers.
- Added explicit brevity, exact-output, marginal-usefulness, and non-invasion stop rules to contain overapplication.
- Added output-quality and trigger evals for category repair, event planning, word pragmatics, prior-knowledge learning, and terse-response controls.
- Fixed validators for reconciled `skill-*` installation paths and added a temporary public-name alias for external `skills-ref` validation.
- Brought UI metadata and icon entries under package-manifest validation.

## 0.4.0

- Added proportional `narrative_support` and auditable `canonical_record` output forms.
- Removed the ordinary-request non-trigger boundary while preventing automatic full-record generation.
- Added a sourced GRADEpro Reference Profile registry with management and test template variants plus `generic.etd`.
- Added academic and software-engineering Domain Packs with source provenance, normative status, scope, selection rules, evidence types, and Canonical Record mappings.
- Added Canonical Schema 3.1.0 while retaining Schema 3.0.0 compatibility.
- Added `profile_id`, `adaptation.domain_pack_ids`, `adaptation.domain_pack_use_case`, compact non-applicable criteria, and single-pack enforcement for new records.
- Limited `for|against` and `strong|conditional` requirements to formal GRADE drafts.
- Added profile inheritance, source, scope, mapping, and pack validation.
- Added resolved inheritance-conflict checks and structured, case-specific certainty-override validation.
- Replaced binary trigger evaluations with output-form, profile, pack, underapplication, overapplication, and metamorphic cases.
- Preserved the three formal claim layers and the prohibition on AI authorization.

## 0.3.0

- Split GRADE evidence assessment, GRADE EtD structural precheck, and formal human authorization.
- Removed `grade_claim_allowed` and all self-authorizing Boolean semantics.
- Allowed formally GRADE-rated health evidence inside a GRADE-informed decision record without claiming formal GRADE EtD.
- Limited the implemented formal GRADE module to comparative health-intervention recommendations.
- Added explicit contrasts and required contrast IDs on effect estimates and certainty assessments.
- Added desirable/undesirable outcome roles, outcome type, and population-importance rationale.
- Added initial and final certainty ratings with domain-based calculation consistency checks.
- Changed artifact verification into integrity, structural-completeness, and methodological-review layers.
- Changed artifacts to declare capabilities satisfied, allowing one report to cover multiple requirements.
- Added explicit criterion evidence bases and criterion-specific judgment-code schemas.
- Added language-neutral machine enums.
- Added Domain Pack versions, hashes, stable candidate IDs, candidate-level selection records, and composition rules.
- Added comprehensive uniqueness and referential-integrity validation.
- Added local artifact path confinement, symbolic-link protection, size limits, extension controls, and remote-reference restrictions.
- Added valid GRADE-evidence/informed-EtD and authorized-import representative cases.
- Expanded failure tests, formal scope tests, security tests, claim-layer tests, and eval definitions.

## 0.2.0

- Repositioned the skill as GRADE-informed by default.
- Separated recommendation process state from direction and strength.
- Added criterion applicability, structured effects, certainty domains, artifact-backed prechecks, governance metadata, and evaluation definitions.
