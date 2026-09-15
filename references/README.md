# 参照資料の構造と意図

このディレクトリには、日常生活や各分野へ概念モデリングを応用する際に使う参照モデルと、親スキルの運用規則を置きます。

- `models/`：分野別モデル、[Generic EtD](models/generic-etd-model.md)、[意思決定モデルへの参照窓口](models/formation-properties.md)。Generic EtD は日常的・分野横断的な評価と報告へ抽象化したモデルとして配置します。
- `models/etd/`：公式 GRADE EtD を志向する文書群。[公式プロファイル](models/etd/official-grade-profiles.yaml)、[方法論上の位置づけ](models/etd/grade-core.md)、[GRADE の表示規則](models/etd/grade-claim-rules.md) をまとめます。
- 直下の運用規則：[モデルの選択](preset-routing.md)、[分野モデルの適用](adaptation-rules.md)、[選択肢形成の連携](question-formation.md)、[回答の拡充](narrative-upscaling.md) を扱います。

基礎となる [概念モデリング](../skills/conceptual-modeling/SKILL.md)、[意思決定構造化](../skills/decision-structuring/SKILL.md)、[文章作成・推敲](../skills/evidence-based-writing/SKILL.md) は、`skills/` の独立サブスキルを参照します。ここではそれらを複製せず、事例へどう適用し、成果へつなげるかを扱います。
