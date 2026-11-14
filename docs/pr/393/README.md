# テンプレート『フォルダ構成』の generated_from.source・tracked を含む design-schemas/v8.3.0 のタグを作成する

## 概要

フォルダ構成の設計書を `generated_from.source`・`tracked` で記載するプロジェクトが、`project-index.yaml` の `ref` をその変更を含む `design-schemas/v8.3.0` へ上げられるようにする。

## 背景

[#392](https://github.com/shuhei1101/knowledge/issues/392) の要望。

- [#377](https://github.com/shuhei1101/knowledge/pull/377)（起点 [#373](https://github.com/shuhei1101/knowledge/issues/373)）で `schemas/design/layout.schema.yaml` に `entries[].generated_from.source`・`generated_from.tracked` を追加し、develop へマージした（squash commit [94717f4](https://github.com/shuhei1101/knowledge/commit/94717f4)）。#377 は反映作業を持たず、タグを作成していない
- 最新のタグ `design-schemas/v8.2.0` は [37932ea](https://github.com/shuhei1101/knowledge/commit/37932ea) を指し、この変更を含まない
- [shuhei1101/alias-inject#107](https://github.com/shuhei1101/alias-inject/issues/107)（作業 PR [shuhei1101/alias-inject#108](https://github.com/shuhei1101/alias-inject/pull/108)）は、タグが無いため `ref` を上げられない

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [反映作業](./反映作業/index.yaml) | develop へマージした後の設計書のスキーマのタグの作成と、依頼元へのタグの名前の連絡 |
