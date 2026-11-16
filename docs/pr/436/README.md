# 選択肢の値のプリセットの規約の追加・module.schema の test_files の拡張・workflow をランナーで確認してからマージする決まりの追加

## 概要

設定・スキーマで選択肢から選ぶ値をプリセットとカスタムで持つ規約を追加し、モジュール構成の `test_files` を実行環境ごとの単体テストのファイルを持てるよう広げ、workflow を触る作業 PR をランナーで動いたことを確認してからマージする決まりと action のバージョンの実在の検査を追加する。

## 背景

束の親 [Issue #434](https://github.com/shuhei1101/knowledge/issues/434) の要望で、次の 3 件を 1 つの作業 PR で行う。

| Issue | 背景 |
| --- | --- |
| [#417](https://github.com/shuhei1101/knowledge/issues/417) | aituber の演出のスキーマの設計で決めた、選択肢から選ぶ値の持ち方（プリセットの階層・参照の書き方・選べる所・カスタム）が knowledge の規約に無い |
| [#426](https://github.com/shuhei1101/knowledge/issues/426) | `schemas/design/module.schema.yaml` の `test_files` が `maxItems: 1` で、Node とブラウザの 2 つの単体テストのファイルを持つ mdmark のモジュールを記載できない（[shuhei1101/mdmark#610](https://github.com/shuhei1101/mdmark/pull/610)） |
| [#430](https://github.com/shuhei1101/knowledge/issues/430) | 存在しないバージョンの action を指定した workflow が、ランナーで一度も動かさないまま develop へ入った（[shuhei1101/ai-monitor#3469](https://github.com/shuhei1101/ai-monitor/pull/3469)・[shuhei1101/ai-monitor#3491](https://github.com/shuhei1101/ai-monitor/pull/3491)） |

#426・#430 はどちらも `schemas/design/` を変えるので、`design-schemas/v*` のタグは束で 1 回作成する。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と変更箇所の由来 |
| [文書](./文書.md) | 文書の計画書 |
