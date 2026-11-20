# 用語集の設計書のスキーマの description を 2 文以内にする

## 概要

用語集の設計書のスキーマの最上位の `description` を 2 文以内にし、結合テスト `test_normal_when_repository_schemas` を pass させる。

## 背景

[Issue #531](https://github.com/shuhei1101/knowledge/issues/531) の報告。
[#446](https://github.com/shuhei1101/knowledge/pull/446) で追加した `schemas/design/glossary.schema.yaml` の最上位の `description` が 3 文あり、設計書のスキーマの `description` を 2 文以内と確かめる結合テストが develop で fail している。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.mark.md) | 要望の整理と変更箇所の由来 |
| [文書](./文書.mark.md) | 文書の計画書 |
