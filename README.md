# grade-informed-etd-decision-support

Version 0.7.0 applies GRADE Evidence-to-Decision principles through two output forms:

- `narrative_support` for ordinary answers and artifacts, with proportional and natural-language decision support;
- `canonical_record` for auditable, machine-readable decisions and optional formal GRADE prechecks.

The skill does not treat every request as a full EtD record. It separates the requested deliverable from the amount of visible decision scaffolding needed.

## Decision Formation

Version 0.7.0 retains the local Decision Formation layer while replacing its
over-specified state model with a small property contract. `context` and
`questions` are the semantic source of truth; `context.sensemaking` remains a flexible
user-oriented narrative, and `alternatives` plus `tree_mermaid` are generated
projections. The exact properties are documented in
`skills/decision-structuring/references/formation-properties.md`.

Narrative Sensemaking, case-specific Research, user Interview, preset reference models such as Domain Packs, and EtD appraisal retain distinct epistemic roles. Research establishes case reality; presets critique coverage; Interview resolves user-specific judgments when material; EtD evaluates formed alternatives and can feed back switching conditions or option-definition defects. Research and Interview are selected as peer epistemic options, but material Interview prompts are normally queued while independent Research and relevant Preset review are completed, then handled in a coherent batch; a dependency may justify a targeted early Interview. The Question Tree and alternatives are derived views rather than independent mutable stores.

This layer is a local GRADE-informed extension, not an official GRADE EtD component. Canonical Schema remains 3.1.0 in this release, and Formation state is not embedded into the Canonical Record. An internal Mermaid diagnostic is generated for every request to catch omissions, but it remains invisible for direct or tightly specified requests. Show it for moderately complex, deep, research-dependent, or explicitly structural requests; do not force Research, Interview, or a visible Formation ritual.

### Reusable decision-structuring subskill

`skills/decision-structuring/SKILL.md` owns the property model and the formation,
Reverse Projection, and correction workflow. It is maintained independently in
`minaph/decision-structuring` and pinned here as a Git submodule. The parent
manifest excludes its files; package validation checks the pinned commit,
initialization, clean checkout, metadata, and local references.

The caller owns request interpretation, research and interviews, appraisal,
and presentation. The subskill returns missing-information needs and material
changes. Generic EtD can consume its results and supply feedback without a
fixed schema mapping. Parent-specific orchestration remains in
`references/question-formation.md`.

Initialize both dependencies with `git submodule update --init --recursive`.
A normal source ZIP does not include their contents. For independent use, clone
`https://github.com/minaph/decision-structuring.git` and register that checkout
as the `decision-structuring` skill. Substantial model-definition work also uses
`conceptual-modeling`, supplied by the caller.

Maintain the independent checkout separately from the parent's pinned checkout.
Commit and push changes in the independent repository, fetch that commit in
`skills/decision-structuring`, check it out, then stage the gitlink and validate
and commit the parent. Do not edit the pinned checkout as a separate copy.

### Formation properties

The internal object has the following deliberately small shape:

```yaml
context:
  description: "free-form domain context"
  sensemaking: "free-form user-oriented narrative"
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

## 概念モデリングスキルの利用と管理

概念モデリングスキルは、`https://github.com/minaph/conceptual-modeling` で独立して管理しています。親スキルは、`skills/conceptual-modeling` にGitサブモジュール（submodule）として配置し、使用するコミットを固定します。`SKILL.md` が入口で、聞き取りの文書と、適用評価・定義・改訂をまとめた文書を参照できます。概念モデリングスキルは、単独でも利用できます。

親スキルは、`references/preset-routing.md` に沿って、モデルの選択と意思決定への反映を担当します。能力質問（CQ）はモデルの表現要件に属し、意思決定の問い（Questions）は現在の状況と作業目的に属します。モデルの選択では、必要な意味との対応、モデル定義の裏付け、事例の情報を分けて確認します。個別の参照モデルには、それぞれの定義と記録形式を適用します。

### 取得と利用

親リポジトリを取得した後は、次のコマンドで固定版の依存先を初期化します。親と依存先を一度に取得する場合は、Gitの再帰的なクローンも利用できます。

```bash
git submodule update --init --recursive
```

完全な利用環境を用意するには、Gitの管理情報を含む作業ディレクトリと、初期化済みのサブモジュールを使います。親のソースZIPや通常の `git archive` には、依存先の内容が含まれません。概念モデリングスキルを単独で使う場合は、リポジトリ全体を利用アプリケーションのスキル探索場所へ配置するか、`SKILL.md` を明示します。サブモジュールとしての配置と、単独スキルとしての登録は、それぞれ行います。

### 使用版の更新

開発用の独立リポジトリと、親スキルが使う固定版の作業ディレクトリを分けて管理します。更新時は、レビューした変更を独立リポジトリでコミットして公開し、親のサブモジュールでそのコミットを取得します。その後、対象コミットへ切り替え、参照コミットを記録するGitリンク（gitlink）をステージして、親側の検証とコミットを行います。通常の利用では、親が記録したコミットを使います。

### 検証と変更前の記録

親のファイルのハッシュ一覧（manifest）と、依存先の固定コミットは分けて検証します。パッケージ検証では、Gitリンク、初期化状態、コミットの一致、未記録の変更、依存先のスキル情報と文書参照を確認します。`skills-ref` パッケージのコマンド（`skills-ref` または `agentskills`）が使える場合は、親と依存先の形式検査も実行します。

親のファイルを変更した後は、`python scripts/update_manifest.py` でハッシュ一覧を更新します。依存先の版を変更した場合は、`git add skills/conceptual-modeling` でGitリンクをステージしてから検証します。検証にはGitの管理情報と、初期化済みのサブモジュールを使います。

旧 `references/model-design.md` と改訂ガイドの内容は、独立スキルと親のモデル選択文書へ引き継ぎました。分離前の文書は、コミット `58ecb5d` で確認できます。

## Generic EtD report model

[Generic EtD model](references/generic-etd-model.md) is the single definition of
report content, evaluation items, evidence and uncertainty, recommendation, and
reporting depth for ordinary requests. Understanding and explanation are also
covered as taking a position. It collects the common reporting guidance
previously spread across the entrypoint and Narrative Upscaling reference.

[Narrative Upscaling](references/narrative-upscaling.md) is a separate rule
for choosing supplementary explanation, examples, experience accounts, and
learning support, including when to stop expanding. It also guides request
interpretation and information gathering. Decision Structuring remains a
separate subskill. Canonical Record formats, official GRADE profiles, and their
validators retain their own scope and compatibility requirements.

## Reference Profiles

`references/official-grade-profiles.yaml` records the public GRADEpro defaults for:

- clinical recommendations from individual and population perspectives;
- coverage decisions;
- health-system and public-health recommendations and decisions;
- test recommendations from individual and population perspectives;
- test coverage decisions.

The registry entry `generic.etd` retains the existing Canonical Record slots
for compatibility. Ordinary report criteria are defined in
`references/generic-etd-model.md`, not by that slot list.

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
