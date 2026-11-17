# 管理用の YAML のスキーマに公開ドキュメントの分類 category を追加する

## 概要

管理用の YAML のスキーマ `schemas/knowledge-files.schema.yaml` の `files[]` の要素に、公開ドキュメントの分類 `category` を追加し、利用側が `nav` の `auto.filter` の `field: category` で絞れるようにする。

## 背景

[Issue #447](https://github.com/shuhei1101/knowledge/issues/447) の要望。
[shuhei1101/voice-paste#329](https://github.com/shuhei1101/voice-paste/issues/329) の `docs/guide/files.yml` の各行は `category`（はじめに・使い方・リファレンス）を持つが、スキーマの `files[].items.properties` に `category` が無い。
project-index は `auto.filter` で使用できる項目を種類のスキーマの `properties` から作るため、`field: category` が `知らない項目です（category）` の警告になり、タブが空になる。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | 文書の計画書 |
