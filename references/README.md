# 参照資料の構造と意図

このディレクトリには、日常生活や各分野へ概念モデリングを応用する際に使う参照モデルと、親スキルの運用規則を置きます。

- `models/`：分野別モデル、[Generic EtD](models/generic-etd-model.md)、[意思決定モデルへの参照窓口](models/formation-properties.md)。Generic EtD は日常的・分野横断的な評価と報告へ抽象化したモデルとして配置します。
- 同じ `models/` に、[レポート構成](models/report-composition.md)、[関係・分類](models/relationship-explanation.md)、[出来事・経験](models/experience-report.md)、[用語](models/term-explanation.md)、[学習](models/learning-explanation.md)、[成果物・手順の利用説明](models/artifact-guide.md) のモデルを置きます。それぞれ単独で使え、必要な組み合わせは運用規則で選びます。
- `models/etd/`：公式 GRADE EtD を志向する文書群。[公式プロファイル](models/etd/official-grade-profiles.yaml)、[方法論上の位置づけ](models/etd/grade-core.md)、[GRADE の表示規則](models/etd/grade-claim-rules.md) をまとめます。
- 直下の運用規則：[モデルの選択](preset-routing.md)、[分野モデルの適用](adaptation-rules.md)、[選択肢形成の連携](question-formation.md) を扱います。

基礎となる [概念モデリング](../skills/conceptual-modeling/SKILL.md)、[意思決定構造化](../skills/decision-structuring/SKILL.md)、[文章作成・推敲](../skills/evidence-based-writing/SKILL.md) は、`skills/` の独立サブスキルを参照します。ここではそれらを複製せず、事例へどう適用し、成果へつなげるかを扱います。

候補の選択には、各ファイル冒頭の `name`（資料名）、`description`（内容と用途）、`kind`（役割）を使います。Markdown は YAML frontmatter、公式プロファイルの YAML は既存のルート項目として保持します。`kind` は `report-model`、`domain-model`、`methodology`、`redirect`、`registry` を区別します。種類は併用を妨げず、適用の判断には候補の本文を読みます。

指示の詳しさにかかわらず同じモデル集合を使い、一般の選択・調査・併用・回答手順は [SKILL.md](../SKILL.md) に従います。メタデータはファイル冒頭の確認や検索で読めます。開発用 Python 環境では `python scripts/list_models.py` で一覧を取得できます。
