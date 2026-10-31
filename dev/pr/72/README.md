# knowledge を dev-docs の配信元として使えるようにし、使い方を書き直す

## 概要

利用者が `/dev-docs:setup` で knowledge を dev-docs の配信元に登録すると、どの端末・プロジェクトからでも規約を画面で読み、dev-docs の MCP に `source: knowledge` を渡して検索・取得できるようになる。

## 背景

[Issue #51](https://github.com/shuhei1101/knowledge/issues/51) の要望。
今は clone して `RULE_INJECT_INDEXES_USER` に `rules.yaml` を書くだけで使い、knowledge のプラグイン・MCP・開発ドキュメントサーバーは無い。
[#64](https://github.com/shuhei1101/knowledge/pull/64)（[#44](https://github.com/shuhei1101/knowledge/issues/44)）で文書を YAML に移した後も、タグやメタデータで規約を引く手段が無い。
スキーマ・参照の検査と CI は、#64 のレビューでこの Issue に含めると決まった（[コメント](https://github.com/shuhei1101/knowledge/pull/64#discussion_r4367269018)）。
開発ドキュメントサーバーと文書の MCP は各リポジトリが作らず、汎用の dev-docs を使うと決まった（[ユーザーの追記](https://github.com/shuhei1101/knowledge/issues/51#issuecomment-6386949622)、D-96〜D-115）。
dev-docs の本体は [shuhei1101/dev-docs#3](https://github.com/shuhei1101/dev-docs/issues/3)・[shuhei1101/dev-docs#4](https://github.com/shuhei1101/dev-docs/issues/4)、規約は [#73](https://github.com/shuhei1101/knowledge/issues/73) が受け持つ。
#73 の規約の改訂で、各リポジトリは文書の MCP のプラグインとマーケットプレイスを持たないと決まり、[#76](https://github.com/shuhei1101/knowledge/issues/76) をこの Issue に統合した。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と影響する UC 一覧 |
| [反映作業](./反映作業/index.yaml) | この端末の dev-docs への knowledge の登録 |

対象システムごとの計画書は、初期構築でアーキテクチャ図のサブシステムを決めた後に追加する。

## タスク一覧

- [x] 初期構築（アーキテクチャ図・非機能要件・設計書の置き場所。コードを持つのはこの PR が初めて）
- [x] ~~リバースエンジニアリング~~（設計書も実装も無く、起こす対象が無い）
- [x] ~~方針決め~~（方針決めを依頼する Issue ではない）
- [ ] PoC 検証（検査のスクリプトが呼ぶ `@probelabs/maid` の `--fix` 無しの検査の出力と終了コード）
- [ ] 複合ユースケース設計
- [x] ~~デザインスタイル選定~~（画面は dev-docs が持ち、mdmark の共通スタイルで描く（D-85・D-96））
- [x] ~~画面一覧・画面遷移~~（画面と画面遷移は dev-docs が持ち、knowledge は `nav` でタブとサイドバーの並びを書くだけ）
- [ ] 単一ユースケース設計
- [x] ~~モック作成~~（画面は dev-docs が持ち、knowledge は画面を作らない）
- [ ] インターフェース定義設計
- [x] ~~部品設計~~（画面の部品は dev-docs と mdmark が持つ）
- [x] ~~画面設計~~（画面の UI 項目は dev-docs が持ち、knowledge の変更は画面の UI 項目を増やさない）
- [ ] モジュール構成設計
- [ ] ドキュメント修正（要件.md の `## 更新ドキュメント`）
- [ ] 単体テスト作成
- [ ] 実装
- [ ] 結合テスト作成
- [ ] E2E テスト作成
