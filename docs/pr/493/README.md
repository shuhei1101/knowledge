# モジュール構成の test_files に、対象の横に配置する React の単体テストのファイルを記載できるようにする

## 概要

モジュール構成の `test_files` に、規約『フォルダ構成』のとおり対象の横に配置した React の単体テストのファイル（`*.test.ts`・`*.test.tsx`）を記載できるようにする。

## 背景

[Issue #492](https://github.com/shuhei1101/knowledge/issues/492) の要望。
develop の `schemas/design/module.schema.yaml` の `test_files` は `pattern: ^tests/.+` で、テストのファイルを `tests/` の下に限っている。
規約『フォルダ構成』（`react-core-folder-structure` の `test-01`）は、unit・結合テストと stories を対象の横に配置すると定めている。
[shuhei1101/ai-monitor#3607](https://github.com/shuhei1101/ai-monitor/pull/3607) で、画面のフロントエンドのモジュール構成 13 件の `test_files` に `frontend/src/...test.ts(x)` を記載すると `does not match '^tests/.+'` の違反になり、`test_files` を記載せずに進めている。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と変更箇所の由来 |
| [文書](./文書.md) | 文書の計画書 |
