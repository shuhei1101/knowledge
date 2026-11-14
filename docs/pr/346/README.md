# 使い方『knowledge を project-index の配信元に登録する』の dev-docs のページへのリンクを docs/guide/ のパスに修正する

## 概要

使い方『knowledge を project-index の配信元に登録する』から、dev-docs の『dev-docsを入れる』『画面で読む』のページを開ける。

## 背景

[Issue #344](https://github.com/shuhei1101/knowledge/issues/344) の要望。作業 PR [#342](https://github.com/shuhei1101/knowledge/pull/342) の作業中に見つかった対象外の不具合。
`docs/guide/guide-setup-docs-mcp.yaml` の dev-docs へのリンク 2 つが、dev-docs の古いパス `docs/使い方/` を指している。dev-docs の develop ではこれらのページが `docs/guide/` に移っていて、今のリンク先にはページが無い。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | 使い方の計画書 |
