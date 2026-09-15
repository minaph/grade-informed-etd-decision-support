# grade-informed-etd-decision-support

Version 0.8.0 は、GRADE EtD を参考にしたレポート形式の概念モデルを用い、日常的・分野横断的な評価、説明、推奨を支援します。依頼された成果物と詳しさに合わせ、根拠、価値判断、条件を説明します。

## Decision Formation

The skill retains the local Decision Formation layer while replacing its
over-specified state model with a small property contract. `context` and
`questions` are the semantic source of truth; `context.sensemaking` remains a flexible
user-oriented narrative, and `alternatives` plus `tree_mermaid` are generated
projections. The exact properties are documented in
`skills/decision-structuring/references/formation-properties.md`.

Narrative Sensemaking, case-specific Research, user Interview, preset reference models such as Domain Packs, and EtD appraisal retain distinct epistemic roles. Research establishes case reality; presets critique coverage; Interview resolves user-specific judgments when material; EtD evaluates formed alternatives and can feed back switching conditions or option-definition defects. Research and Interview are selected as peer epistemic options, but material Interview prompts are normally queued while independent Research and relevant Preset review are completed, then handled in a coherent batch; a dependency may justify a targeted early Interview. The Question Tree and alternatives are derived views rather than independent mutable stores.

This layer is a local GRADE-informed extension, not an official GRADE EtD component. An internal Mermaid diagnostic is generated for every request to catch omissions, but it remains invisible for direct or tightly specified requests. Show it for moderately complex, deep, research-dependent, or explicitly structural requests; do not force Research, Interview, or a visible Formation ritual.

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
separate subskill.


## 分野別の参照モデル

ドメインパックは自然言語の参照モデルです。対象と比較単位、判断に必要な概念の区別、根拠と適用限界を示します。

- [学術研究](references/domain-academic.md): 課題の優先順位、研究資源の配分、計画の質、成果の共有。
- [ソフトウェア工学](references/domain-software-engineering.md): 構成・技術の選定、変更方針、安全な開発、品質のトレードオフ。
- [教育](references/domain-education.md): 学習成果、参加機会、教育実践と方針。
- [健康・医療](references/domain-health.md): 健康アウトカム、医療、公衆衛生、提供体制。
- [組織・製品・業務](references/domain-organization.md): 利用者と働く人への価値、負担の分布、実施能力。

候補の全件評価や保存欄への対応づけは求めません。複数分野が関わる場合は、[適用の指針](references/adaptation-rules.md) に沿って対象と概念の意味を照合します。外部資料から得た観点とローカルな整理、事例について得た根拠を区別します。

## GRADE 関連資料

[公式プロファイル](references/official-grade-profiles.yaml) は、GRADEpro の公開テンプレートについて、臨床、償還、保健医療システム・公衆衛生、検査の用途と視点の違いを示す参照情報です。汎用レポートの必須項目を定めたり、方法論的な適合性を自動判定したりするものではありません。

GRADE 評価済みの根拠を使ったこと、今回の検討方法、人による承認は分けて説明します。[方法論上の位置づけ](references/grade-core.md) と [表示の指針](references/grade-claim-rules.md) を参照してください。

## 検証

文書を利用するだけなら Python は不要です。開発時の検証には Python 3.10+、`requirements.txt` の依存パッケージ、および `skills-ref` または `agentskills` を用意します。

```bash
python -m pip install -r requirements.txt
python scripts/update_manifest.py
python scripts/validate_profiles.py
python scripts/validate_evals.py
python -m unittest discover -s tests -p 'test_*.py'
python scripts/validate_skill_package.py --require-skills-ref
```

検証対象は、パッケージ情報、ローカル文書の参照、依存先の固定版、ハッシュ一覧、公式プロファイルの参照情報、評価ケースの定義です。意思決定の内容や正式 GRADE の方法論的適合性を承認する検証ではありません。モデルを実行する評価の実施状況は [EVAL_STATUS.md](EVAL_STATUS.md) に記載します。

## 0.8.0 での廃止

Canonical Record、その保存形式、専用バリデーター、正式 GRADE の自動事前検査、旧形式の互換性検査を廃止しました。変更の影響と旧版の参照方法は [MIGRATION.md](MIGRATION.md) を確認してください。
