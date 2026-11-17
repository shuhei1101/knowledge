# 用語集の設計書のスキーマを追加し、flowchart の clicks[].href の説明を id: のリンクに限る

## 概要

各プロジェクトがリポジトリ固有の用語集を設計書のスキーマで記載できるように `schemas/design/glossary.schema.yaml` を追加し、設計書の `clicks[].href` の説明を `id:` のリンクだけにそろえる。

## 背景

[Issue #445](https://github.com/shuhei1101/knowledge/issues/445) は、どちらも `schemas/design/` を変えて `design-schemas/v*` のタグを打つ次の 2 件の束。

- [#444](https://github.com/shuhei1101/knowledge/issues/444): [shuhei1101/claude-balancer#329](https://github.com/shuhei1101/claude-balancer/pull/329) で用語集（`alias_type: term`）を作るため、用語集のスキーマを knowledge に追加してもらう案に決定した。`schemas/terms.schema.yaml` は knowledge に登録する用語だけを記載するスキーマで、リポジトリ固有の用語には使用できない。claude-balancer の作業 PR を待たせている
- [#443](https://github.com/shuhei1101/knowledge/issues/443): [shuhei1101/ai-monitor#3558](https://github.com/shuhei1101/ai-monitor/pull/3558) で、AI Monitor の設計書の検証が mermaid の `click` の相対パスのリンクを誤りとして返却するようになる。今の `clicks[].href` の説明と例は相対パス + アンカーを含んでいる

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | 文書の計画書 |
