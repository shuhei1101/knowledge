# シナリオの図を mdmark の map で記載するスキーマにし、テンプレート『シナリオ』とシナリオの設計書の図を移す

## 概要

シナリオを書く人が、`flow` の図を mdmark の map（Mermaid と補足）で記載でき、テンプレート『シナリオ』とシナリオの設計書に map でない Mermaid の図が残らない状態にする。

## 背景

[#246](https://github.com/shuhei1101/knowledge/issues/246) の要望。

- [#210](https://github.com/shuhei1101/knowledge/issues/210) の書き直しの判断で、シナリオの図の置き換えを切り出した。D-373 A で、シナリオの図は mdmark の新しい図 map（[shuhei1101/mdmark#324](https://github.com/shuhei1101/mdmark/issues/324)。D-51）が入ってから map で記載すると決まった
- 依存の #210（[#252](https://github.com/shuhei1101/knowledge/pull/252)）は適用済みで、mdmark#324 は [shuhei1101/mdmark#445](https://github.com/shuhei1101/mdmark/pull/445) で develop へ入った
- 後続の [#146](https://github.com/shuhei1101/knowledge/issues/146)（maid の検査の削除）は、シナリオに Mermaid が残る間は進められない
- インターフェース定義の `flow` とモジュール構成の `diagrams[].diagram` は [#251](https://github.com/shuhei1101/knowledge/issues/251) が扱う

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | 文書の計画書 |
| [反映作業](./反映作業/index.yaml) | develop へマージした後の設計書のスキーマのタグの作成 |
