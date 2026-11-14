# GitHub Actions の workflow のテストの配置 tests/e2e/workflow/ を、規約『V字モデル』の対応表と統一する

## 概要

workflow のインターフェース定義のテストを作る人が、規約『V字モデル』・規約『GitHub Actions の workflow のテスト』・テンプレート『インターフェース定義』のどれを参照しても、同じ場所にテストのファイルを配置できるようにする。

## 背景

[Issue #389](https://github.com/shuhei1101/knowledge/issues/389) の要望。
規約『V字モデル』（`dev-v-model` の `mapping-01`）はインターフェース定義のテストを `tests/integration/{サブシステム名}/` に配置すると定め、workflow の例外を記載していない。
規約『GitHub Actions の workflow のテスト』・規約『テストの種類と配置』・テンプレート『インターフェース定義』の記載例 2・`schemas/design/interface.schema.yaml` の例は `tests/e2e/workflow/` に配置する。
`tests/e2e/workflow/` は [#362](https://github.com/shuhei1101/knowledge/issues/362)（作業 PR [#378](https://github.com/shuhei1101/knowledge/pull/378)）で入り、[#380](https://github.com/shuhei1101/knowledge/issues/380) の作業 PR [#386](https://github.com/shuhei1101/knowledge/pull/386) でスコープ外として切り出した。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と変更箇所の由来 |
| [文書](./文書.md) | 文書の計画書 |
