# 配信元の設定に使う場面（when）を記載する

## 概要

knowledge の配信元の設定に `when` を記載し、エージェントが `describe` の一覧と文書の MCP の instructions から、knowledge で検索する場面を読み取れるようにする。

## 背景

[#315](https://github.com/shuhei1101/knowledge/issues/315) の要望。

- shuhei1101/project-index#39（作業 PR shuhei1101/project-index#55）で、配信元の設定に省略できるキー `when` が追加された。`describe` の一覧・説明書に全ての行、文書の MCP の instructions の配信元の一覧に 1 行目が出る
- #315 は shuhei1101/project-index#55 のスコープ外から切り出した Issue。依存の shuhei1101/project-index#39 は close 済みで、端末の project-index のクローン（develop）のスキーマは `when` を持つ

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | 文書の計画書 |
