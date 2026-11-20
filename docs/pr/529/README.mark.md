# 規約『FastAPI の認証とエラー』の exception-handler-04 の 1 文を、文の長さの上限に収める

## 概要

規約『FastAPI の認証とエラー』の項目 `exception-handler-04` の 1 文を、意味を変えずに 100 文字以内の文に分け、全ての文書の検査が違反 0 件で終わるようにする。

## 背景

[Issue #528](https://github.com/shuhei1101/knowledge/issues/528) の要望。
[#522](https://github.com/shuhei1101/knowledge/pull/522)（[13e609f](https://github.com/shuhei1101/knowledge/commit/13e609f)）で入った `exception-handler-04` の `body` の 1 文が 147 文字あり、全ての文書の検査が develop で textlint の `sentence-length`（上限 100 文字）の違反 1 件・終了コード 1 で終わる。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.mark.md) | 要望の整理 |
