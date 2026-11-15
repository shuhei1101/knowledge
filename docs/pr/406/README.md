# テンプレート『インターフェース定義』の workflow の記載例を、全ての文書の検査の突き合わせに通る記載へ修正する

## 概要

テンプレート『インターフェース定義』の workflow の記載例 IF-2 を、全ての文書の検査（IF-72-3）の workflow の突き合わせに通る記載へ修正する。

## 背景

[#405](https://github.com/shuhei1101/knowledge/issues/405) の要望。
記載例 IF-2「テストの全件実行」は [#356](https://github.com/shuhei1101/knowledge/pull/356) で入り、突き合わせ（`scripts/_workflow.py` の `check_request`・`_compare_overall`）は後から入った。
記載例は `request[layer].type` が `unit / integration`・`overall_flow` にジョブの `subgraph` が無い・判定のノード `q{全ての step が成功したか}` を持つため、記載例のとおりに記載すると突き合わせが違反を出す。
[#404](https://github.com/shuhei1101/knowledge/pull/404) の IF-352-1 は同じ指摘で修正済み（[レビューの指摘](https://github.com/shuhei1101/knowledge/pull/404#discussion_r4576733090)）。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と変更箇所の由来 |
| [文書](./文書.md) | 文書の計画書 |
