# テンプレート・規約・設計書のスキーマの記載の書き換えと、x-used-by の検査・確認の状態のキーの追加・判定フローチャートの参照の追加をまとめて行う

## 概要

テンプレート・規約・設計書のスキーマの記載を書き換え、全ての文書の検査に `x-used-by` の検査を、外部 API・外部ライブラリのスキーマにパラメータごとの確認の状態のキーを、テンプレート `agent_flow`・`evaluation` に判定フローチャートの参照を追加する。

## 背景

束の親 Issue [#322](https://github.com/shuhei1101/knowledge/issues/322) の要望。
子 Issue [#254](https://github.com/shuhei1101/knowledge/issues/254)・[#269](https://github.com/shuhei1101/knowledge/issues/269)・[#286](https://github.com/shuhei1101/knowledge/issues/286)・[#294](https://github.com/shuhei1101/knowledge/issues/294)・[#311](https://github.com/shuhei1101/knowledge/issues/311)・[#317](https://github.com/shuhei1101/knowledge/issues/317) は、どれも `schemas/design/` か `docs/template/` を触る。
前提だった PR [#271](https://github.com/shuhei1101/knowledge/pull/271)・[#275](https://github.com/shuhei1101/knowledge/pull/275)・[#277](https://github.com/shuhei1101/knowledge/pull/277)・[#291](https://github.com/shuhei1101/knowledge/pull/291) は develop に入っている。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | スキーマ・テンプレート・規約・`dev-docs.yaml`・`rules.yaml` の計画書 |
| [検査と変換のスクリプト](./検査と変換のスクリプト.md) | `scripts/check_all.py` の計画書 |
