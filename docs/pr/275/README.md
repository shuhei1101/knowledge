# 設計書のテンプレート（agent・mcp_server・agent_flow・launch・llm_call・evaluation・eval_criterion・eval_case）を schemas/design に追加する

## 概要

各プロジェクトが、LLM のエージェント・MCP サーバー・エージェントフロー・起動の構成・LLM の呼び出し・精度評価を、knowledge の設計書のテンプレートで同じ書式で設計できるようにする。

## 背景

[Issue #224](https://github.com/shuhei1101/knowledge/issues/224) の要望。`schemas/design/` には、ツールを使用して手順を進めるエージェントと、モデルを 1 回呼ぶ処理を設計するテンプレートが無く、aituber のブレインノードや AI Monitor の planner を設計するとき、プロジェクトごとに書式がばらばらになる。
起票後の追記（[精度評価の追加](https://github.com/shuhei1101/knowledge/issues/224#issuecomment-6708721148)・[案の変更](https://github.com/shuhei1101/knowledge/issues/224#issuecomment-6709331400)・[手順の索引と部品の id](https://github.com/shuhei1101/knowledge/issues/224#issuecomment-6710230981)・[modes の削除と headers](https://github.com/shuhei1101/knowledge/issues/224#issuecomment-6711371838)・[agent_flow への改名とスキルの統合](https://github.com/shuhei1101/knowledge/issues/224#issuecomment-6769159832)）で、対象は 8 種類と、テンプレート『スキル』の統合になった。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | 文書の計画書（スキーマ・テンプレート・スキル・配信の設定） |
| [検査と変換のスクリプト](./検査と変換のスクリプト.md) | 検査と変換のスクリプトの計画書（テンプレートの生成の対応表） |
