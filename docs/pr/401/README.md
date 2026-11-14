# テンプレート『フォルダ構成』で、convention のフォルダでも生成物・複製のエントリを children に記載できるようにする

## 概要

フォルダ構成の設計書の作り手が、`convention` で規約を指すフォルダの中にある生成物・複製のエントリを、`children` に記載できるようになる。

## 背景

[Issue #400](https://github.com/shuhei1101/knowledge/issues/400) の要望。
`schemas/design/layout.schema.yaml` の `x-rules` は「`convention` のフォルダは `children` を記載しない」と定めるが、`examples` の `src/aituber` は `convention` と `children` を両方持ち、スキーマの検査も両方を持つことを禁じていない。
`x-rules` のとおりに読むと、`convention` のフォルダの中にある git で管理する生成物（`generated_from` を記載するエントリ）を記載する場所が無くなる。
[shuhei1101/claude-balancer#299](https://github.com/shuhei1101/claude-balancer/pull/299) の作業で見つかった。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と変更箇所の由来 |
| [文書](./文書.md) | 文書の計画書 |
