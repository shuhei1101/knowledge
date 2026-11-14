# インターフェース定義の flow の description を 2 文以内にし、ER図・状態遷移の設計書から Mermaid を生成できるようにする

## 概要

インターフェース定義のスキーマの `flows[].flow` の description を 2 文以内にして結合テストを合格させ、ER図・状態遷移の設計書から Mermaid の `erDiagram`・`stateDiagram-v2` を生成できるようにする。

## 背景

[#365](https://github.com/shuhei1101/knowledge/issues/365) は [#364](https://github.com/shuhei1101/knowledge/issues/364)・[#363](https://github.com/shuhei1101/knowledge/issues/363) を 1 本の作業 PR で行う束。

- #364: develop（9937ab8）で結合テスト `tests/integration/scripts/test_check_all.py::test_normal_when_repository_schemas` が fail する。`schemas/design/interface.schema.yaml` の `flows[].flow` の description が 3 文ある。進行中の [#146](https://github.com/shuhei1101/knowledge/issues/146)（作業 PR [#337](https://github.com/shuhei1101/knowledge/pull/337)）の結合テストの合格に関わる
- #363: [shuhei1101/mdmark#565](https://github.com/shuhei1101/mdmark/issues/565) から切り出した要望。mdmark の map は ER 図・状態遷移図を描けるようになったが、設計書から Mermaid を生成する決まり・仕組みが無い

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と変更箇所の由来 |
| [文書](./文書.md) | 文書（スキーマ・テンプレート）の計画書 |
| [検査と変換のスクリプト](./検査と変換のスクリプト.md) | 検査と変換のスクリプトの計画書 |
