# schemas/ の design・meta・word-list・template のスキーマの文言を AI slop の単語の対応表に合わせ、設計書のテンプレートを再生成する

## 概要

- `schemas/design/` と `schemas/` の meta・word-list・template のスキーマの文言を、AI slop の単語の対応表に合わせて統一する
- 設計書のスキーマから生成する設計書のテンプレートを、修正した文言で再生成する

## 背景

[Issue #241](https://github.com/shuhei1101/knowledge/issues/241) の要望。
[PR #240](https://github.com/shuhei1101/knowledge/pull/240)（起点 [Issue #238](https://github.com/shuhei1101/knowledge/issues/238)）は [#236](https://github.com/shuhei1101/knowledge/issues/236) の prompt・common・files の 3 ファイルだけを対象にし、同じ型の文言が残る他のスキーマをこの Issue へ切り出した。
`schemas/skill.schema.yaml` は [#224](https://github.com/shuhei1101/knowledge/issues/224) が削除するため対象から外す（[task-planner の連絡](https://github.com/shuhei1101/knowledge/issues/241#issuecomment-6769524489)）。
[PR #243](https://github.com/shuhei1101/knowledge/pull/243) の結合テストで、`schemas/design/module.schema.yaml` の `test_files` の `description` が 3 文で `test_normal_when_repository_schemas` が fail することが分かり、この Issue の対象に追加した（[コメント](https://github.com/shuhei1101/knowledge/issues/241#issuecomment-6743020649)）。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と影響する UC 一覧 |
| [文書](./文書.md) | 文書の計画書 |
| [反映作業](./反映作業/index.yaml) | develop へマージした後の設計書のスキーマのタグの作成 |
