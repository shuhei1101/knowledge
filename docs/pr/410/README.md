# インターフェース定義のスキーマの overall_flow の x-rules に、subgraph とノードの決まりを追加する

## 概要

インターフェース定義のスキーマの `overall_flow` の `x-rules` に、全ての文書の検査（IF-72-3）の突き合わせが求める `subgraph` とノードの決まりを追加し、テンプレート『インターフェース定義』を再生成する。

## 背景

[#407](https://github.com/shuhei1101/knowledge/issues/407) の要望。
突き合わせ `scripts/_workflow.py` の `_compare_overall` は、`overall_flow` の `subgraph` とジョブを 1 対 1 で比べるが、`x-rules` は step の `name` と分岐の判定の 2 行だけで、決まりを示すのは記載例 IF-2 だけになっている。
[#406](https://github.com/shuhei1101/knowledge/pull/406) で記載例 IF-2 を直したときにスコープ外へ切り出した（[レビューの指摘](https://github.com/shuhei1101/knowledge/pull/406#discussion_r4576823445)）。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と変更箇所の由来 |
| [文書](./文書.md) | 文書の計画書 |
