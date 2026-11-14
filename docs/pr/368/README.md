# GitHub Actions の workflow の静的な検査（actionlint と、インターフェース定義と workflow のファイルの突き合わせ）を決める

## 概要

GitHub Actions の workflow を持つプロジェクトが、actionlint を lint の層で回し、インターフェース定義と workflow のファイルが食い違っていないかをレビューで突き合わせられるようにする。

## 背景

[Issue #361](https://github.com/shuhei1101/knowledge/issues/361) の要望。作業 PR [#356](https://github.com/shuhei1101/knowledge/pull/356)（起点 Issue [#355](https://github.com/shuhei1101/knowledge/issues/355)）のスコープ外の切り出しで、元は [#351](https://github.com/shuhei1101/knowledge/issues/351) の「静的な検査の案」。
#356 で、入口が `trigger` の workflow をインターフェース定義の `overall_flow`・`flows[].flow` のフローチャートで記載する書式が develop へ入った。
今は workflow のファイル自体の検査の決まりが無く、設計書との突き合わせもレビュー観点が step の `name` だけを見ている。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | 文書の計画書 |
