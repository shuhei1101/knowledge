# スキーマ『共通』の ER 図の関連の from_column・to_column の x-used-by の外部キーの向きを、例と設計書に合わせる

## 概要

スキーマ『共通』の ER 図の関連の `from_column`・`to_column` の `x-used-by` を、例と設計書の外部キーの向きに合わせる。

## 背景

[Issue #385](https://github.com/shuhei1101/knowledge/issues/385) の要望。shuhei1101/dev-docs#210 のレビューの対象外の逸脱の報告から起票された。
`schemas/design/common.schema.yaml` の `from_column` の `x-used-by` は「外部キーの列」、`to_column` は「外部キーが参照する列」としているが、`schemas/design/er.schema.yaml` の例（`from_column: ID`・`to_column: user_id`）と AI Monitor の ER 図の設計書は逆の向きで記載している。
`title`・`description` は [11150b1](https://github.com/shuhei1101/knowledge/commit/11150b1) で「元の列」「先の列」に直っている。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と変更箇所の由来 |
| [文書](./文書.md) | 文書の計画書 |
