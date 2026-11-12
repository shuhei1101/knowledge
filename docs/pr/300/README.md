# dev-docs の文書の MCP のツールの完全名を、project-index のプラグインの名前に書き換える

## 概要

knowledge が書いている dev-docs の文書の MCP のツールの完全名を、project-index のプラグインの完全名に書き換え、プラグイン slop-check が移した後の `write_docs` も照合する。

## 背景

[Issue #276](https://github.com/shuhei1101/knowledge/issues/276) の要望。
[shuhei1101/project-index#15](https://github.com/shuhei1101/project-index/pull/15)（マージ済み）で、dev-docs の文書の MCP・管理の MCP が project-index のプラグイン `project-index` へ移り、ツールの完全名が `mcp__plugin_project-index_project-index__{ツール名}`・`mcp__plugin_project-index_project-index-admin__{ツール名}` に変わった。
knowledge はスキル text-review・プラグイン slop-check・その設計書・テストで今の完全名を書いている。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [slop-check](./slop-check.md) | slop-check の計画書 |
| [文書](./文書.md) | 文書の計画書 |
