# rules.yaml に、write_docs で設計書を書き込むときに種類ごとのスキーマを案内する行を追加し、knowledge の文書を指すエントリに read_tool を記載する

## 概要

エージェントが `write_docs` で設計書を書き込むときに種類ごとのスキーマの参照を案内され、knowledge の規約の案内を受けたときに YAML を Read せずに project-index の `search_docs` で参照できるようになる。

## 背景

[#395](https://github.com/shuhei1101/knowledge/issues/395) は、[#194](https://github.com/shuhei1101/knowledge/issues/194) と [#205](https://github.com/shuhei1101/knowledge/issues/205) を 1 本の作業 PR で行う束。
どちらも直下の `rules.yaml` に、rule-inject の `read_tool`（[shuhei1101/rule-inject#100](https://github.com/shuhei1101/rule-inject/issues/100)・[#102](https://github.com/shuhei1101/rule-inject/pull/102)）を使う行・キーを追加する。

- #194: [PR #359](https://github.com/shuhei1101/knowledge/pull/359) で設計書の種類のフォルダのファイルを Edit・Write するときの案内は入ったが、`write_docs` で書き込むときの案内が無い
- #205: develop の `rules.yaml` の全てのエントリに `read_tool` が無く、YAML の規約を Read で開くと「search_docs で読んでください」の案内が出て 2 回読むことになっている（[ユーザーのコメント](https://github.com/shuhei1101/knowledge/issues/205#issuecomment-6847483389)）

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | 文書の計画書 |
