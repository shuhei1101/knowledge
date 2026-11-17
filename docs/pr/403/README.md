# 規約『ルール索引への登録』の read_tool の記載の 2 文を 100 文字以内に分ける

## 概要

規約『ルール索引への登録』の `read_tool の記載` の 2 文を 100 文字以内の文に分け、全ての文書の検査に合格させる。

## 背景

[#402](https://github.com/shuhei1101/knowledge/issues/402) の要望。
[#401](https://github.com/shuhei1101/knowledge/pull/401) の全ての文書の検査（`scripts/check_all.py`）で、`docs/rule/dev-rule-index-registration.yaml` の `index-writing-14` の 2 文が textlint の `ja-technical-writing/sentence-length`（上限 100 文字）に違反して終了コード 1 になった（170 文字・155 文字）。
記載は [#398](https://github.com/shuhei1101/knowledge/pull/398) の [0e3c606](https://github.com/shuhei1101/knowledge/commit/0e3c606) で入った。
develop に残る間は、作業 PR ごとの検査のログに範囲の外のこの違反が出る。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | 文書の計画書 |
