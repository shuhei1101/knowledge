# dev-docs.yaml の tags を - name: の要素で持つ種類に tags: tags[].name の対応を記載する

## 概要

エージェントが dev-docs の `search_docs` で knowledge の文書のタグを、`topic:フロントエンド` などのタグの名前で絞り込み・集計できるようになる。

## 背景

[Issue #139](https://github.com/shuhei1101/knowledge/issues/139) の要望。
knowledge の規約などは `tags` を `- name: topic:...` の要素（オブジェクトの配列）で持つが、`dev-docs.yaml` の `documents[]` に `metadata` の `tags` の対応が無い。
dev-docs はタグを文字列の配列として読むため、`search_docs` の `group_by: tags` が `"{'name': 'topic:フロントエンド'}"` のように辞書を文字列にした値で返す。
このため rule-inject の `check_indexes` が、使われている `topic:*`・`scope:*` のタグのパターンを「使われていない」と誤って報告する（[shuhei1101/rule-inject#95](https://github.com/shuhei1101/rule-inject/issues/95)）。
`metadata` の `tags: tags[].name` の書き方は [shuhei1101/dev-docs#43](https://github.com/shuhei1101/dev-docs/issues/43) で入り、[shuhei1101/dev-docs#50](https://github.com/shuhei1101/dev-docs/pull/50) で dev-docs の develop へマージ済み。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と影響する UC 一覧 |
| [文書](./文書.md) | 文書の計画書 |

## タスク一覧

- [x] ~~初期構築~~（既存リポジトリのため対象外）
- [x] ~~リバースエンジニアリング~~（現状の設計書が揃っている）
- [x] ~~方針決め~~（方針決めを依頼する Issue ではない）
- [x] ~~PoC 検証~~（dev-docs#43 で入った `metadata` の書き方を使うだけで、未検証の技術機構に依存しない）
- [x] ~~複合ユースケース設計~~（影響なし: 規約を引く流れは変わらない）
- [x] ~~デザインスタイル選定~~（画面を持たない）
- [x] ~~画面一覧・画面遷移~~（画面を持たない）
- [ ] 単一ユースケース設計
- [x] ~~モック作成~~（画面を持たない）
- [x] ~~インターフェース定義設計~~（検査と変換のスクリプト・CI の入出力は変わらない）
- [x] ~~部品設計~~（画面を持たない）
- [x] ~~画面設計~~（画面を持たない）
- [x] ~~モジュール構成設計~~（スクリプトの関数・型は変わらない）
- [x] ~~ドキュメント修正~~（規約・使い方の記述は変わらない。要件.md の `## 更新ドキュメント` はなし）
- [x] ~~単体テスト作成~~（スクリプトのコードは変わらない）
- [ ] 実装
- [x] ~~結合テスト作成~~（スクリプトのコードは変わらない）
- [ ] E2E テスト作成
