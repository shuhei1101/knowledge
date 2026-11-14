# インターフェース定義の flow とモジュール構成の図を mdmark の図で記載するスキーマにし、テンプレートと設計書の図を移す

## 概要

インターフェース定義とモジュール構成を書く人が、`flows[].flow` と `diagrams[].diagram` の図を mdmark の図で記載でき、テンプレートと設計書に map の外の Mermaid の図が残らない状態にする。

## 背景

[#251](https://github.com/shuhei1101/knowledge/issues/251) の要望。

- [#210](https://github.com/shuhei1101/knowledge/issues/210) の書き直しの判断で切り出した。契機は shuhei1101/ai-monitor#3363 で、配布先の設計書でこの 2 つの図を mdmark の図で記載できない（実例 shuhei1101/gui-support#96）
- シナリオの `flow` は [#272](https://github.com/shuhei1101/knowledge/pull/272)（[#246](https://github.com/shuhei1101/knowledge/issues/246)）で `common.schema.yaml` の `$defs/map` を参照する形になった。インターフェース定義の `flow` とモジュール構成の `diagrams[].diagram` は `$defs/mermaid` を参照したまま
- 後続の [#146](https://github.com/shuhei1101/knowledge/issues/146)（maid の検査の削除）と [#248](https://github.com/shuhei1101/knowledge/issues/248) は、この PR を待つ

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | 文書の計画書 |
| [反映作業](./反映作業/index.yaml) | develop へマージした後の設計書のスキーマのタグの作成 |
