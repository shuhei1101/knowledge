# 用語集のスキーマの用語に、詳細のページを指す任意のキーを追加する

## 概要

用語集の文書を記載する人が、用語ごとに、その用語を説明するページへのリンクを記載できるようになる。

## 背景

[Issue #525](https://github.com/shuhei1101/knowledge/issues/525) の要望。
用語集のスキーマ（`schemas/terms.schema.yaml`）の用語（`$defs.term`）は `additionalProperties: false` で、`id`・`name`・`description`・`aliases`・`avoid` だけを持ち、用語を説明するページへのリンクを入れるキーが無い。
mdmark は用語集の表を用語の YAML から描くように変え（[shuhei1101/mdmark#753](https://github.com/shuhei1101/mdmark/pull/753)）、今の表の `詳細` の列（158 件のうち 154 件がガイドのページへのリンク）も用語の YAML から出すとユーザーが決めた（[確認事項](https://github.com/shuhei1101/mdmark/pull/753#discussion_r4640374456)）。
mdmark は用語集のスキーマを `design-schemas/v*` のタグで指すため、キーを追加した後にタグを上げる。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.mark.md) | 要望の整理 |
| [文書](./文書.mark.md) | 文書（用語集のスキーマ）の計画書 |
| [反映作業](./反映作業/index.yaml) | 設計書のスキーマのタグの作成 |
