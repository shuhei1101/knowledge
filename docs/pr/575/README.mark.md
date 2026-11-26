# 設計書のスキーマから Markdown のテンプレート（雛形と記載例）を生成する

## 概要

Markdown を原本にして設計書を書くプロジェクトが、設計書の種類ごとの Markdown のテンプレート（雛形と記載例）をスキーマから生成したファイルで使用できるようになる。

## 背景

[Issue #574](https://github.com/shuhei1101/knowledge/issues/574) の要望。
設計書のテンプレートは YAML の設計書を書くための `docs/template/template-{種類}.yaml`（`scripts/build_templates.py` がスキーマから生成し、`scripts/check_all.py` が一致を確認する）しか無く、dev-docs を使用できないプロジェクトが Markdown で設計書を書くときに従うテンプレートが無い。
設計書の YAML を Markdown にする変換は dev-docs の `schema_to_markdown` が持っている。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.mark.md) | 要望の整理 |
| [検査と変換のスクリプト](./検査と変換のスクリプト.mark.md) | Markdown のテンプレートの生成と一致の確認の計画書 |
| [文書](./文書.mark.md) | 生成物の配置と dev-docs での配信の計画書 |
| [CI](./CI.mark.md) | テストの全件実行のワークフローの計画書 |
