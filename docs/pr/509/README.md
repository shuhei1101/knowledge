# 使い方『knowledge のプラグインを入れる』の概要の 2 文を 1 行 1 文に分ける

## 概要

使い方『knowledge のプラグインを入れる』の概要の 1 行に並ぶ 2 文を 1 行 1 文に分け、全ての文書の検査を違反なしで通す。

## 背景

[#508](https://github.com/shuhei1101/knowledge/issues/508) の要望。
[#505](https://github.com/shuhei1101/knowledge/pull/505) で `docs/guide/guide-setup-install-plugin.yaml` の `overview` の `body` の 2 行目に 2 文が並び、全ての文書の検査（`scripts/check_all.py`）が textlint の `one-sentence-per-line` の違反 1 件で終了コード 1 になる。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | サブシステム「文書」の計画書 |
