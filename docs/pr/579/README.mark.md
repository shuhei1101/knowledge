# agent_flow.schema.yaml の 2 文を超える description を 2 文以内にし、スキーマの結合テストを pass させる

## 概要

`schemas/design/agent_flow.schema.yaml` の 2 文を超える `description` を 2 文以内にし、結合テスト `test_check_all.py::test_normal_when_repository_schemas` を pass させる。

## 背景

[Issue #578](https://github.com/shuhei1101/knowledge/issues/578) の不具合。
develop（`83e01b6`）で、`schemas/design/` の全てのスキーマの `description` が 2 文以内かを確認する結合テストが fail する。
[#567](https://github.com/shuhei1101/knowledge/pull/567) が `$defs/step` に追加した `id`・`unit` の `description` が 3 文以上になっている。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.mark.md) | 要望の整理と変更箇所の由来 |
| [文書](./文書.mark.md) | 文書（スキーマ・テンプレート）の計画書 |
| [反映作業](./反映作業/index.yaml) | マージの後の設計書のスキーマのタグの作成 |
