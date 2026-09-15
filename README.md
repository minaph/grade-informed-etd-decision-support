# 概念モデリングの実務応用

概念モデリング技術を基礎として、その日常生活や他分野への応用を扱うスキルです。状況や概念を整理し、参照モデルを実際の事例へ適用するとともに、意思決定やレポート作成まで支援します。モデリングを実務的に日常利用する際に必要となる、情報収集、選択肢の整理、評価、説明の関心をつなぐことを目的とします。

Version 0.9.0。スキル識別子とリポジトリ名は、既存の参照との互換性のため `grade-informed-etd-decision-support` を維持しています。入口は [SKILL.md](SKILL.md) です。

## 意思決定として扱う立場

このスキルは、日常的な話題や多分野の話題を、基本的に意思決定として扱う立場を採用しています。知的な話題でも、どの観点から理解し、どの説明や概念定義を採用するかを「ある立場をとる」という行為・判断として扱います。この接続を、概念モデリングを実務の関心に応用する際の中心に置きます。

これは、このスキルが支援する対象と方法の選択です。あらゆる知的活動が本質的に意思決定であると主張するものではありません。指示の背後にある意思決定構造を推定し、明示されていない目標や価値も仮説として補って推論・調査を進めます。非・意思決定的な関心には助力できませんが、この探索を行うスキル自身によるスコープ判断には限界があります。詳細な指示から非・意思決定的な解釈を求めていることが明確になって初めて、対象外と判断します。基礎となる概念モデリング技術そのものの適用範囲を、この境界に限定するものでもありません。

意思決定として扱うことは、毎回の回答に比較表や行動提案を追加することを意味しません。説明や定義そのものが、採用した立場を表す成果物になります。事実認定は根拠に従い、出力の詳しさは依頼に合わせます。

この立場の選択に関する設計判断は、本 README と [docs/](docs/README.md) に記録します。`docs/` は設計の検討・改訂用であり、通常利用時の参照ルートには含めません。理由と適用境界は [意思決定を軸とする実務応用](docs/decision-oriented-application.md) にまとめています。

## サブスキルの役割

| サブスキル | 担当する技術 |
| --- | --- |
| [conceptual-modeling](skills/conceptual-modeling/SKILL.md) | 概念モデルの要件整理、適合性の評価、定義、適用、改訂の基礎 |
| [decision-structuring](skills/decision-structuring/SKILL.md) | Context、Questions、Alternatives、Tree による意思決定の構造化 |
| [evidence-based-writing](skills/evidence-based-writing/SKILL.md) | 主張、根拠、条件、用語、文章構造を保った文書作成と推敲 |

親スキルは、利用目的に合うモデルと技術を選び、調査・聞き取りと成果物への反映を担当します。文章作成のサブスキルは、与えられた根拠を正確に伝えるために使います。必要な資料の収集や、個別の主張の検証を代替しません。

## 参照モデルと運用規則

資料の構造と設置意図は [references/README.md](references/README.md) にまとめています。`models/` には分野モデルと Generic EtD、`models/etd/` には公式 GRADE EtD を志向する文書群を置きます。

[Generic EtD](references/models/generic-etd-model.md) は、評価・比較・推奨を報告するためのモデルです。[Narrative Upscaling](references/narrative-upscaling.md) は、背景、具体例、経験、学習支援をどこまで加えるかという別規則です。文章の記述品質には `evidence-based-writing` を使います。モデルの定義だけを求める依頼などに、評価や推奨を一律に追加しません。

## 依存先の取得と管理

三つのサブスキルは独立したリポジトリで管理し、親は Git サブモジュールとして使用コミットを固定します。取得後に次を実行してください。

```bash
git submodule update --init --recursive
```

通常のソース ZIP にはサブモジュールの内容が含まれません。Git の管理情報と初期化済みの依存先を含む作業ディレクトリを利用してください。

`evidence-based-writing` の独立リポジトリは `minaph/evidence-based-writing` です。今回のローカル登録では、`~/.agents/skills/evidence-based-writing` から `~/Projects/evidence-based-writing` を参照します。親は `skills/evidence-based-writing` の固定版を使うため、独立チェックアウトの更新が親へ自動反映されることはありません。

更新は独立リポジトリでレビュー・コミット・公開した後、親のサブモジュールで対象コミットを取得して切り替えます。変更した Git リンクをステージし、親のハッシュ一覧とパッケージを検証します。親の manifest はサブモジュール内のファイルを含めず、依存先は固定コミットとして別に検査します。

## 意思決定構造化との連携

選択肢の形成には [親の連携手順](references/question-formation.md) を使います。Context と Questions を元に、Alternatives と Mermaid Tree を生成します。Context は description、sensemaking、objects の順に整理します。プロパティの正式な定義は独立サブスキルに置きます。

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

`actions: []` は未解決の問いを表し、探索中の選択肢はゼロまたは一つでも構いません。実際の比較には、内容と単位のそろった二つ以上の候補が必要です。利用者の自然言語による訂正を Context または Questions へ反映し、投影を再生成します。

親は各依頼で最小の内部 Tree を用いて区別の不足を確認します。直接的な回答や固定形式の依頼では表示せず、この診断だけを理由に調査、聞き取り、比較や評価を追加しません。

## 検証と適用限界

文書を使うだけなら Python は不要です。開発時の検証には Python 3.10+、`requirements.txt` の依存パッケージ、および `skills-ref` または `agentskills` を用います。

```bash
python -m pip install -r requirements.txt
python scripts/update_manifest.py
python -m unittest discover -s tests -p 'test_*.py'
python scripts/validate_skill_package.py --require-skills-ref
```

検証はパッケージ情報、文書参照、依存先の固定版、ハッシュ一覧、公式プロファイルと評価ケースの定義を対象にします。モデルの判断品質や GRADE の方法論的適合性、人による承認を保証するものではありません。実施した評価と限界は [EVAL_STATUS.md](EVAL_STATUS.md)、旧保存形式の廃止は [MIGRATION.md](MIGRATION.md) を参照してください。
