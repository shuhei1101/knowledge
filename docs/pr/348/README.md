# 設計書のスキーマへの tags・aliases と管理用の YAML のキーの取り込み・design-schemas のタグと、検索・配信の持ち主を dev-docs とする記述の修正をまとめて行う

## 概要

AI Monitor と各プロジェクトが、knowledge の `schemas/design/` と `schemas/knowledge-files.schema.yaml` をタグで参照し、自分のコピーを持たずに `tags`・`aliases` と管理用の YAML の `id`・`aliases`・`inject_when` を記載できるようにする。あわせて、スキーマとテンプレートの検索・配信の持ち主の記述を project-index にする。

## 背景

[#347](https://github.com/shuhei1101/knowledge/issues/347)（[#336](https://github.com/shuhei1101/knowledge/issues/336)・[#345](https://github.com/shuhei1101/knowledge/issues/345) の束）の要望。

- #336: shuhei1101/ai-monitor#3430 で AI Monitor は設計書のスキーマのコピーを削除して knowledge の原本を参照する。コピーにしかない `tags`・`aliases`（shuhei1101/ai-monitor#3379）と `files.items` の `id`・`aliases`・`inject_when`（shuhei1101/ai-monitor#3375）を原本へ取り込み、タグを打つ
- #345: [#342](https://github.com/shuhei1101/knowledge/pull/342) で文書の MCP と配信元の登録の持ち主が project-index になったが、`schemas/design/` と生成したテンプレートに dev-docs の記述が残っている

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | 文書の計画書 |
| [反映作業](./反映作業/index.yaml) | develop へマージした後の設計書のスキーマのタグの作成と AI Monitor への連絡 |
