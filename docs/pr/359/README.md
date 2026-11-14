# rules.yaml に、設計書の種類のフォルダのファイルへ schemas/design の Schema を案内する行を加える

## 概要

設計書の種類のフォルダのファイルを書くエージェントが、rule-inject の案内で knowledge の `schemas/design/{種類}.schema.yaml` を読めるようになる。

## 背景

[#358](https://github.com/shuhei1101/knowledge/issues/358) の要望。
[shuhei1101/ai-monitor#3430](https://github.com/shuhei1101/ai-monitor/pull/3430) で AI Monitor は設計書の Schema のコピーを削除し、knowledge の `schemas/design/` を参照する形へ移る。
AI Monitor の `rules.global.yaml` はそのコピーを案内していたが、`rule` は索引ファイルからの相対パスのため knowledge のファイルを指せない。
`global.indexes` に載っている knowledge の `rules.yaml` へ案内の行を移す。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
