# 設計書のスキーマのキーを設ける条件を meta.schema.yaml に追加し、schemas/design のキーを見直す

## 概要

設計書のスキーマを作る人とレビュアーが、どのキーも実装かレビューのどこで使用するかを確認でき、使用先の無いキーが無い状態にする。

## 背景

[#217](https://github.com/shuhei1101/knowledge/issues/217) の要望。

- `schemas/meta.schema.yaml` の `x-rules` は各項目に `title`・`description` を付けることを決めているが、キーを設ける条件を決めていない
- 条件が無いため、aituber のテンプレートの案で、使用先の無いキー（`limits`・`updated`）・ほかの設計書と二重のキー（`mcp_servers`・`tools[].when`）・1 つの値に 2 つの事柄を入れるキー（`model`・`prompt_files`）・値で表せない事柄を持つキー（`tools[].type`）ができた
- 規約『表し方の優先順位』は設計書のテンプレートのキーの表に使用先の列を求めているが、スキーマに使用先を持つ場所が無く、生成したテンプレートに列が無い
- 依存の [#210](https://github.com/shuhei1101/knowledge/issues/210)（[#252](https://github.com/shuhei1101/knowledge/pull/252)）は適用済み。[#215](https://github.com/shuhei1101/knowledge/issues/215) はこの PR の後に見直したキーを点検する

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | 文書の計画書 |
| [検査と変換のスクリプト](./検査と変換のスクリプト.md) | 検査と変換のスクリプトの計画書 |
| [反映作業](./反映作業/index.yaml) | develop へマージした後の設計書のスキーマのタグの作成 |
