# 種類「ノウハウ」のスキーマを追加し、flowchart の clicks[].href の説明に id: のリンクを追加する

## 概要

種類「ノウハウ」（`knowhow`）のスキーマを `schemas/` に追加し、設計書のスキーマの共通の型 `flowchart` の `clicks[].href` に `id:` のリンクを書けることを説明と例に追加する。

## 背景

[Issue #437](https://github.com/shuhei1101/knowledge/issues/437) は、どちらも `schemas/` を触る次の 2 件の束。

- [#419](https://github.com/shuhei1101/knowledge/issues/419): [#418](https://github.com/shuhei1101/knowledge/issues/418)（ノウハウの種類の追加と、規約のうち知見に当たるものの移動）の受付判断で、スキーマの設計を切り出した。#418 はこのスキーマを前提に着手する
- [#432](https://github.com/shuhei1101/knowledge/issues/432): [shuhei1101/dev-docs#241](https://github.com/shuhei1101/dev-docs/pull/241) で、dev-docs の画面の変換が `clicks` の `href` の `id:` を解決するようになる。今の `href` の説明は「押したときに開く先（相対パス + アンカー）。」だけで、`id:` のリンクを書けることが分からない

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | 文書の計画書 |
