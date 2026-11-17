# 配信元 knowledge の検索の対象とメタデータを project-index の setup の推奨の範囲と付け方に合わせる

## 概要

エージェントが、knowledge の YAML でないファイル（`README.md`・`CLAUDE.md`・スキーマ・テスト・プラグインなど）も project-index の文書の MCP で検索・取得できるようになる。

## 背景

[Issue #462](https://github.com/shuhei1101/knowledge/issues/462) の要望。
project-index の setup が推奨する検索の範囲（`**/*`）と、仮のメタデータの付け方（ファイルの中身を段階的に参照して付ける）が project-index の develop に入った（[shuhei1101/project-index#101](https://github.com/shuhei1101/project-index/issues/101)・[shuhei1101/project-index#102](https://github.com/shuhei1101/project-index/issues/102)）。
knowledge の `project-index.yaml` の `documents[]` と管理用の YAML（`skills/files.yaml`・`scripts/files.yaml` だけ）は、それより前の範囲と付け方のままになっている。
直下と `docs/` 直下のファイルを管理用の YAML に記載できるようにする変更（[shuhei1101/project-index#133](https://github.com/shuhei1101/project-index/issues/133)）は close 済みで、手元の project-index の配信は develop で動いている。
project-index 自身の配信元の同じ見直しは [shuhei1101/project-index#132](https://github.com/shuhei1101/project-index/pull/132) で済んでいる。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | サブシステム『文書』の計画書 |
