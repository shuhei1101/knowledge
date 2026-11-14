# GitHub Actions の workflow のフローを pytest から gh で確認するテストの書き方の規約を追加する

## 概要

入口が `trigger` の GitHub Actions の workflow のインターフェース定義のフロー 1 つを、pytest から `gh` を呼ぶテストの関数 1 つにする書き方を規約に定める。

## 背景

[#362](https://github.com/shuhei1101/knowledge/issues/362) の要望。
[#356](https://github.com/shuhei1101/knowledge/pull/356)（束 [#355](https://github.com/shuhei1101/knowledge/issues/355)）のスコープ外から切り出された。元は [#351](https://github.com/shuhei1101/knowledge/issues/351) の本文の「フローからテストへの置き換えの案」。
#356 で、テンプレート『インターフェース定義』に workflow のフロー（`overall_flow`・`flows[].flow` の `flowchart`）と、テストのファイルを `tests/e2e/workflow/` に配置する記載例が入った。
テンプレート『テスト実行方法』の `run_runner` の記載例に、`gh workflow run`・`gh run watch --exit-status`・`gh run view` の呼び方が既にある。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | 文書のサブシステム（規約・ルールの索引）の計画書 |
