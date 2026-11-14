# 公開文書の配信のワークフロー（IF-137-2）を、workflow のフローチャートと全体の流れで記載し直す

## 概要

公開文書の配信のワークフロー（IF-137-2）を読む人が、workflow がどの step を通り、どこで失敗するかを図から読み取れるようにする。

## 背景

[#360](https://github.com/shuhei1101/knowledge/issues/360) の要望。作業 PR [#356](https://github.com/shuhei1101/knowledge/pull/356) のスコープ外の切り出し。

- IF-137-2 の 3 つのフローの図は `participant` を並べた `sequenceDiagram` で、workflow の条件と分岐が図から読み取れない
- #356 で、入口が `trigger` のインターフェース定義に、通る step だけを並べた一本道の `flowchart` と、省略できる全体の流れ（`overall_flow`）の書式が追加された（`design-schemas/v8.2.0`）

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と変更箇所の由来 |
| [文書](./文書.md) | 文書の計画書 |
