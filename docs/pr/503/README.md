# 規約『ルール索引への登録』の read_tool の記載の、設計書のスキーマを指すエントリの文を、文の長さの上限に収める

## 概要

規約『ルール索引への登録』の項目『read_tool の記載』（`index-writing-14`）の、設計書のスキーマを指すエントリの文を分け、全ての文書の検査の違反を 0 件にする。

## 背景

[Issue #502](https://github.com/shuhei1101/knowledge/issues/502) の要望。
この文は [#499](https://github.com/shuhei1101/knowledge/pull/499) で入れたもので、115 文字あり、全ての文書の検査（`uv run --frozen --script scripts/check_all.py`）で textlint の `ja-technical-writing/sentence-length`（上限 100 文字）の違反になる。
develop の [34c6731](https://github.com/shuhei1101/knowledge/commit/34c6731) で検査すると、違反はこの 1 件だけで、終了コード 1 で終わる。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と変更箇所の由来 |
| [文書](./文書.md) | 文書の計画書 |
