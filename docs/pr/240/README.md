# schemas/ の設計書の本文の型に contentMediaType を追加し、プロンプトの kind にエージェントのシステムプロンプトを追加して、prompt・common・files の文言を対応表に合わせる

## 概要

- dev-docs の `write_docs` が、設計書の本文を書き込む前に mdmark で点検できるようにする
- エージェントのシステムプロンプトを、プロンプトファイルとして記載・検査できるようにする
- prompt・common・files のスキーマの文言を、AI slop の単語の対応表に合わせて統一する

## 背景

[Issue #238](https://github.com/shuhei1101/knowledge/issues/238) がまとめる、`schemas/` を変更する 3 件の要望。

- [#197](https://github.com/shuhei1101/knowledge/issues/197): `schemas/design/common.schema.yaml` の `$defs/markdown` に `contentMediaType` が無く、[shuhei1101/dev-docs#111](https://github.com/shuhei1101/dev-docs/issues/111) の点検が設計書の本文に適用されない。knowledge の文書のスキーマには [#195](https://github.com/shuhei1101/knowledge/pull/195) で追加済み
- [#226](https://github.com/shuhei1101/knowledge/issues/226): 規約『プロンプトファイル』の `kind` は `llm`・`hook`・`instructions`・`tool` で、`--append-system-prompt` で指定するエージェントのシステムプロンプトの種類が無い。起動の構成（[#224](https://github.com/shuhei1101/knowledge/issues/224) の `launch`）の `system_prompt` が指すファイルの `kind` を決められない
- [#236](https://github.com/shuhei1101/knowledge/issues/236): dev-docs の `templates/` のコピーの文言は [shuhei1101/dev-docs#148](https://github.com/shuhei1101/dev-docs/pull/148) で対応表に合わせたが、原本の knowledge の `schemas/` に修正前の文言が残っている

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と影響する UC 一覧 |
| [文書](./文書.md) | 文書の計画書 |
| [反映作業](./反映作業/index.yaml) | develop へマージした後の設計書のスキーマのタグの作成 |
