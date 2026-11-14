# dev-yaml の Mermaid の検査と scripts の maid の検査を削除する

## 概要

knowledge の文書の検査から maid による mermaid の文法の検査を外し、規約『YAML』の mermaid の検査の決まりを削除する。

## 背景

[#146](https://github.com/shuhei1101/knowledge/issues/146) の要望。

- [#134](https://github.com/shuhei1101/knowledge/pull/134) の要件.md のスコープ外から切り出した。#134 は規約『表し方の優先順位』を追加し、Mermaid の規約を廃止した
- [#272](https://github.com/shuhei1101/knowledge/pull/272)・[#333](https://github.com/shuhei1101/knowledge/pull/333) で、シナリオ・インターフェース定義・モジュール構成のテンプレートと設計書から map の外の Mermaid の図が無くなった。図は mdmark の map の中の Mermaid で記載する

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | 文書の計画書 |
| [検査と変換のスクリプト](./検査と変換のスクリプト.md) | 検査と変換のスクリプトの計画書 |
