# 文書の Markdown への変換で、種類に固有の入れ子のキーをスキーマの title で描く

## 概要

利用者が画面で文書を開いたとき、種類に固有の入れ子のキー（オブジェクトの中の配列・オブジェクトの配列・列挙）を、JSON の文字列やキー名ではなく、スキーマの `title` を使用した箇条書きと表で参照できるようになる。

## 背景

[Issue #452](https://github.com/shuhei1101/knowledge/issues/452) の要望。
作業 PR [#451](https://github.com/shuhei1101/knowledge/pull/451)（起点 [#418](https://github.com/shuhei1101/knowledge/issues/418)）で作ったノウハウの文書を [scripts/knowledge_markdown.py](https://github.com/shuhei1101/knowledge/blob/e965883/scripts/knowledge_markdown.py)（IF-72-2）で変換すると、`scenes` の中の配列が JSON の文字列のまま 1 行に出て、`cases[]`・`evidence[]` の表の列名がキー名のままになり、`necessity`・`confidence` は値だけが出る。
スキーマの `title` を使用するのは最上位のキーの見出しだけで、入れ子のキーの扱いは種類によらない。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と変更箇所の由来 |
| [検査と変換のスクリプト](./検査と変換のスクリプト.md) | 検査と変換のスクリプトのサブシステムの計画書 |
