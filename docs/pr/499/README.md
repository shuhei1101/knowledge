# rules.yaml の Schema のエントリの read_tool を、案内のとおり呼べば Schema の本文が返る記載にする

## 概要

`rules.yaml` で設計書の Schema（`schemas/design/{種類}.schema.yaml`）を案内するエントリの `read_tool` を、案内のとおり呼べば Schema の本文が返る記載にする。

## 背景

[Issue #498](https://github.com/shuhei1101/knowledge/issues/498) の要望。
Schema のエントリの `read_tool` は `mcp__plugin_project-index_project-index__describe` を `{"kind": "{種類}"}` だけで呼ぶ案内になっており、そのとおり呼ぶと project-index が `InvalidArgumentError: kind には source が要ります` で断る。
この記載は [#398](https://github.com/shuhei1101/knowledge/pull/398) で入れたもので、規約『ルール索引への登録』の項目『read_tool の記載』が `source` を書き込む側のプロジェクトで変わるため記載しないと定めている。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と変更箇所の由来 |
| [文書](./文書.md) | 文書の計画書 |
