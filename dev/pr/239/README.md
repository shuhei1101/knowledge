# 単一 UC『エージェントが knowledge の文書を書き込む』に、mdmark の点検で書き込みを止める異常シナリオを追加する

## 概要

単一 UC『エージェントが knowledge の文書を書き込む』に、Markdown の本文の値が mdmark の点検で警告を出すときに書き込まない異常シナリオを追加する。

## 背景

[Issue #198](https://github.com/shuhei1101/knowledge/issues/198) の要望。依頼元は [#195](https://github.com/shuhei1101/knowledge/pull/195) の要件の `## スコープ外`。
#195 で knowledge の文書のスキーマの Markdown の本文のキーに `contentMediaType: text/markdown` を追加し、dev-docs の `write_docs` がその値を `mdmark check --text -` で点検するようになった（[shuhei1101/dev-docs#111](https://github.com/shuhei1101/dev-docs/pull/111)）。
シナリオは正常・検査のスクリプトが違反を返す・`scope.write` の外の 3 つだけを持ち、mdmark の点検で書き込みを止める場合を持たない。
E2E テストの追加は、2026-11-09 のユーザーの依頼（[計画 Issue のコメント](https://github.com/shuhei1101/knowledge/issues/1#issuecomment-6726836084)）で範囲から外した。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と影響する UC 一覧 |
| [文書](./文書.md) | 文書の計画書 |
| [反映作業](./反映作業/index.yaml) | マージの後に端末へ mdmark の CLI を入れる作業 |
