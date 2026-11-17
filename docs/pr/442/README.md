# mdmark の参照を既定で develop の最新にし、設定でバージョンを固定できるようにする

## 概要

開発者と CI が、全ての文書の検査と Pages の成果物の作成で、タグを待たずに mdmark の develop へ入った機能を使用できるようになる。
設定でタグか commit の SHA を指定すれば、その参照に固定できる。

## 背景

[#427](https://github.com/shuhei1101/knowledge/issues/427) の要望。
mdmark をタグ（`v0.13.0`）に固定して参照しており、mdmark の新規の機能を使用する作業 PR [#396](https://github.com/shuhei1101/knowledge/pull/396) が、mdmark のタグを打つ [mdmark#571](https://github.com/shuhei1101/mdmark/issues/571) を待って止まった。
mdmark の側は [mdmark#620](https://github.com/shuhei1101/mdmark/issues/620)（[mdmark#621](https://github.com/shuhei1101/mdmark/pull/621) でマージ済み）で、`npx github:shuhei1101/mdmark#develop` で develop の最新を呼べるようになった。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と変更箇所の由来 |
| [検査と変換のスクリプト](./検査と変換のスクリプト.md) | 検査と変換のスクリプトの設計書・実装・テストの計画書 |
| [文書](./文書.md) | 外部ライブラリ・開発コマンド・テンプレートの計画書 |
