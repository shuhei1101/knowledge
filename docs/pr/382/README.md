# 規約『トップレベルレイアウト + feature 内構造』のトップレベルに、デスクトップの画面の入口 ui/ を加える

## 概要

デスクトップの画面（GUI・トレイ）を持つ Python プロジェクトが、画面の入口を規約に定めた `ui/` に配置できるようにする。

## 背景

[Issue #381](https://github.com/shuhei1101/knowledge/issues/381) の要望。依頼元は voice-paste の作業 PR [shuhei1101/voice-paste#309](https://github.com/shuhei1101/voice-paste/pull/309)。
規約『トップレベルレイアウト + feature 内構造』の `top-level-01` のトップレベルには入口として `server/` と `{command}/` だけがあり、デスクトップの画面の入口を配置するフォルダが無い。
voice-paste は `src/voice_paste/ui/` に Qt の画面・トレイを持ち、import-linter の層の契約で `server` と `ui` を同じ層の入口にしている。
層の依存の向きは規約『依存方向のルール』が定めており、その図の最上位の層も `features / server` だけを持つ。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | 文書の計画書 |
