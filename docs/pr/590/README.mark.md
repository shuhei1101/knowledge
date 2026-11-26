# screen.schema.yaml の count_limit.type の description を 2 文以内にし、スキーマの結合テストを pass させる

## 概要

`schemas/design/screen.schema.yaml` の `count_limit.type` の `description` を 2 文以内にし、結合テスト `test_check_all.py::test_normal_when_repository_schemas` を pass させる。

## 背景

[Issue #588](https://github.com/shuhei1101/knowledge/issues/588) の不具合。
develop（`0f5168b`）で、`schemas/design/` の全てのスキーマの `description` が 2 文以内かを確認する結合テストが fail する。
[#585](https://github.com/shuhei1101/knowledge/pull/585) が追加した `count_limit.type` の `description` は、括弧の中の「。」を含めて 3 文と判定される。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.mark.md) | 要望の整理と変更箇所の由来 |
| [文書](./文書.mark.md) | 文書（スキーマ・テンプレート）の計画書 |
| [反映作業](./反映作業/index.yaml) | マージの後の設計書のスキーマのタグの作成 |
