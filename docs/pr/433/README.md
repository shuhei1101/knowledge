# 設計書のスキーマの refs の要素を、関連の種類 type と参照する条件 when を持つ関連の要素へ変える

## 概要

`schemas/design/` の設計書のスキーマの `refs` の要素を、参照の文字列から、関連先の ID（`to`）・関連の種類（`type`）・いつ参照するか（`when`）を持つ関連の要素へ変え、メジャーを上げた設計書のスキーマのタグを作成する。

## 背景

[Issue #429](https://github.com/shuhei1101/knowledge/issues/429) の要望。
今の設計書の `refs` は `{ID}#{項目のパス}` の文字列だけで、規約『ドキュメント管理』の「関連」（`related-01`〜`related-05`）が求める関係の種類といつ参照するかを持てず、project-index の `trace_related` で関連をたどれない。
依頼元は [shuhei1101/ai-monitor#3534](https://github.com/shuhei1101/ai-monitor/pull/3534)（起点 Issue [shuhei1101/ai-monitor#3042](https://github.com/shuhei1101/ai-monitor/issues/3042)）で、このタグを前提に、前のタグの設計書を変換するバージョンアップ変換と、`type`・`when` の検証を作る。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と変更箇所の由来 |
| [文書](./文書.md) | 文書の計画書 |
