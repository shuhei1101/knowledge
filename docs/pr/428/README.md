# 文書のマーカーを mdmark の JSON の記載へ移す

## 概要

knowledge の文書と変換のスクリプトが書く mdmark のマーカーを、今の書き方（`キー=値`・`+機能`・位置の値）から JSON の記載へ移し、`mdmark check` が `legacy_mark` を出さない状態にする。

## 背景

[Issue #316](https://github.com/shuhei1101/knowledge/issues/316) の要望。
mdmark の [shuhei1101/mdmark#477](https://github.com/shuhei1101/mdmark/pull/477) でマーカーの設定を JSON のオブジェクトで記載できるようになり、今の書き方を参照する処理は [shuhei1101/mdmark#479](https://github.com/shuhei1101/mdmark/issues/479) で削除される。
依頼元は [shuhei1101/mdmark#520](https://github.com/shuhei1101/mdmark/pull/520)（起点 Issue [shuhei1101/mdmark#478](https://github.com/shuhei1101/mdmark/issues/478)）。
前提の mdmark v0.11.0 の配布（[shuhei1101/mdmark#528](https://github.com/shuhei1101/mdmark/issues/528)）と、`design_docs publish` が JSON の記載を書き出す修正（[shuhei1101/ai-monitor#3418](https://github.com/shuhei1101/ai-monitor/issues/3418)）は close 済み。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | 文書の計画書 |
| [検査と変換のスクリプト](./検査と変換のスクリプト.md) | 検査と変換のスクリプトの計画書 |
