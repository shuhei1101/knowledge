# 狭い幅で画面の短い文言が折り返す・省略されるときの対処の判定フローチャートを追加し、規約『レイアウト』『入力と文言』から参照する

## 概要

画面を設計・レビューする人が、狭い幅でヘッダーの文字と画面の短い文言（通知・ボタン・ラベル・見出し）が折り返す・省略されるときに、どの対処を選ぶかを判定フローチャートで決められるようにする。

## 背景

[Issue #594](https://github.com/shuhei1101/knowledge/issues/594) の要望。
[shuhei1101/ai-monitor#3851](https://github.com/shuhei1101/ai-monitor/pull/3851) で扱う [shuhei1101/ai-monitor#2113](https://github.com/shuhei1101/ai-monitor/issues/2113)（統合した [shuhei1101/ai-monitor#2114](https://github.com/shuhei1101/ai-monitor/issues/2114)）の判定フローチャートを、画面を持つ全てのプロジェクトの規約と同じ knowledge に配置すると決めた。
ai-monitor の planner『モック作成』『設計』の画面設計と reviewer の画面の確認がこの判定フローチャートを参照するため、shuhei1101/ai-monitor#3851 はこの PR を待っている。
規約『レイアウト』（`ui-layout`）の `pitfall-text-code-04`・`pitfall-text-code-05` は長さが変わる値の折り返しと省略の既定を持つが、短い固定の文言そのものが収まらないときの対処の選び方は、『レイアウト』にも『入力と文言』（`ui-input-wording`）にも無い。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.mark.md) | 要望の整理 |
| [文書](./文書.mark.md) | 文書の計画書 |
