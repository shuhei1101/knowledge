# テスト実行方法のスキーマの notes に、画面の起動のセクションの記載方法を加える

## 概要

配布先の planner が、テスト実行方法の補足に `画面の起動` のセクション（画面ごとの起動・閲覧 URL の得方・止め方の表）を、スキーマの記載方法に沿って記載できるようにする。

## 背景

[Issue #592](https://github.com/shuhei1101/knowledge/issues/592) の要望。
AI Monitor の reviewer『レビュー』と planner『実装』は、実装した画面を開くときにテスト実行方法の `notes` の `画面の起動` を参照する（[shuhei1101/ai-monitor#3848](https://github.com/shuhei1101/ai-monitor/pull/3848) で参照先を統一した）。
`schemas/design/test_procedure.schema.yaml` の `notes` は共通の `notes` を参照するだけで `画面の起動` の書き方を示さないため、配布先の planner がセクションを記載できなかった（[shuhei1101/ai-monitor#3227](https://github.com/shuhei1101/ai-monitor/issues/3227)、実例 [shuhei1101/gui-support#81](https://github.com/shuhei1101/gui-support/pull/81)）。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.mark.md) | 要望の整理 |
| [文書](./文書.mark.md) | 文書の計画書 |
