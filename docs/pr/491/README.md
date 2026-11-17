# 共通の型 ref と refs[].item の pattern を、[...] の中の対応の取れた [ ] を値の一部にする参照の型の項目のパスに追随させる

## 概要

設計書の参照の型（`{ID}#{項目のパス}`）と関連の `refs[].item` の `pattern` を、`[...]` の中の対応の取れた `[` `]` を値の一部にする IF-6 の書き方に合わせる。

## 背景

[Issue #490](https://github.com/shuhei1101/knowledge/issues/490) の要望。
[shuhei1101/project-index#169](https://github.com/shuhei1101/project-index/pull/169) で、`write_docs` の参照の型の項目のパスは `[...]` の中の対応の取れた `[` `]` を値の一部として読むようになった（IF-6 の制約「参照の型の項目のパス」）。
この書き方は設計書の参照の型の `#` から後と同じ。
develop の `schemas/design/common.schema.yaml` の `ref` と `related_item` の `item` の `pattern` は `[...]` の中の `]` を許可しない。
`[...]` の外の `]` を許可するため `IF-6#request[operations[].fields].description` は一致するが、対応の取れない `[` `]` を含む値も一致する。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と変更箇所の由来 |
| [文書](./文書.md) | 文書の計画書 |
