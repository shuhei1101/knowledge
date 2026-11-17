# 規約『GitHub Actions の workflow のテスト』の手順 3 の文を 100 字以内に分け、全ての文書の検査の文の長さの違反をなくす

## 概要

全ての文書の検査を流すエージェントが、規約『GitHub Actions の workflow のテスト』の文の長さの違反を受け取らずに、作業 PR の違反だけを確認できるようにする。

## 背景

[Issue #482](https://github.com/shuhei1101/knowledge/issues/482) の要望。
[#479](https://github.com/shuhei1101/knowledge/pull/479)（[8ec57dc](https://github.com/shuhei1101/knowledge/commit/8ec57dc62e7e6b2b5c95d30a138290e73a281fae)）が steps-01 に入れた手順 3 の文が 109 字で、全ての文書の検査の textlint `ja-technical-writing/sentence-length`（1 文 100 字まで）の違反になる。
違反は develop にあるため、全ての作業 PR の全ての文書の検査に同じ 1 件が出る（[#475](https://github.com/shuhei1101/knowledge/pull/475) で対象外の逸脱として切り出した）。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と変更箇所の由来 |
| [文書](./文書.md) | 文書の計画書 |
