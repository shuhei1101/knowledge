# knowledge の文書ごとに案内の場面を決め、rule-inject の索引と文書のエイリアス・照合条件に登録する

## 概要

knowledge の文書を、使用する場面（ファイルを書く前・ツールを呼ぶ前・会話にその話題が出たとき）で Claude Code に案内されるようにする。

## 背景

[Issue #158](https://github.com/shuhei1101/knowledge/issues/158) の要望。
11-03 の develop の調査（R-5）で、文書の多くが `rules.yaml` にも `aliases` にも無く、使用する場面で案内されていない。

- 判定フローチャート『タグの付与』『用語の登録』『エイリアスの登録』『関連の張り方』『単語の選び方』と、Next.js・HTML などスタック別の規約が案内されない
- `aliases` を持つ文書が `dev-local-server` の 1 件だけで、alias-inject の照合は文書の名前だけ。「フォルダ構成」「Security」「YAML」のような一般語の名前が、関係の無い作業でも当たる
- 文書を MCP（dev-docs の `write_docs`・ai-monitor の `write_design_doc_*`・MindStella の `add`・`update`・`batch`）で書き込むときに、規約『タグと用語の登録』が当たらない（統合した [#67](https://github.com/shuhei1101/knowledge/issues/67)）

依存の [#82](https://github.com/shuhei1101/knowledge/issues/82) で `rules.yaml` に載せる基準が強制注入の 4 つの基準になり、[#157](https://github.com/shuhei1101/knowledge/issues/157) で判定表『エイリアスを登録しない条件』に照合条件 `inject_when` の分岐が入った。
rule-inject は [shuhei1101/rule-inject#100](https://github.com/shuhei1101/rule-inject/issues/100) でエントリごとの `read_tool` を、alias-inject は [shuhei1101/alias-inject#57](https://github.com/shuhei1101/alias-inject/issues/57) で文書ごとの `inject_when` を持った。
knowledge の文書への `inject_when` の記載（[shuhei1101/alias-inject#61](https://github.com/shuhei1101/alias-inject/issues/61)）と、[#145](https://github.com/shuhei1101/knowledge/issues/145) の文書の `aliases` の付与は、この Issue へ統合された。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と影響する UC 一覧 |
| [文書](./文書.md) | 文書の計画書 |
| [検査と変換のスクリプト](./検査と変換のスクリプト.md) | 検査と変換のスクリプトの計画書 |

## タスク一覧

- [x] ~~初期構築~~（既存リポジトリのため対象外）
- [x] ~~リバースエンジニアリング~~（設計書が揃っている）
- [x] ~~方針決め~~（方針決めを依頼する Issue ではない）
- [x] ~~PoC 検証~~（未検証の技術機構に依存しない。`args`・`inject_when` の評価は rule-inject・alias-inject の設計書とテストで確認でき、`read_tool` は入っている rule-inject の版が読めないことをコードで確認したため、版を依存にした）
- [x] ~~複合ユースケース設計~~（案内の設定が増えるだけで、ユースケースの流れを変えない）
- [x] ~~デザインスタイル選定~~（利用者に見える画面を変えない）
- [x] ~~画面一覧・画面遷移~~（画面の追加・削除と画面遷移の変更を含まない）
- [x] ~~単一ユースケース設計~~（シナリオの手順を変えない。変換が `inject_when` を本文に出さないことはインターフェース定義の制約で持つ）
- [x] ~~モック作成~~（利用者に見える画面を変えない）
- [x] インターフェース定義設計
- [x] ~~部品設計~~（変更が画面に及ばない）
- [x] ~~画面設計~~（変更が画面に及ばない）
- [ ] モジュール構成設計
- [ ] ドキュメント修正（要件.md の `## 更新ドキュメント`）
- [ ] 単体テスト作成
- [ ] 実装
- [ ] 結合テスト作成
- [ ] E2E テスト作成
