# knowledge を開発ドキュメントサーバーと文書の MCP のプラグイン（HTTP）で使えるようにし、使い方を書き直す

## 概要

利用者が、knowledge を clone して開発ドキュメントサーバーを起動し、文書の MCP のプラグイン `knowledge-docs` を入れると、どの端末・プロジェクトからでも規約を MCP で検索・取得・書き込みできるようになる。

## 背景

[Issue #51](https://github.com/shuhei1101/knowledge/issues/51) の要望。
今は clone して `RULE_INJECT_INDEXES_USER` に `rules.yaml` を書くだけで使い、knowledge のプラグイン・MCP・開発ドキュメントサーバーは無い。
[#64](https://github.com/shuhei1101/knowledge/pull/64)（[#44](https://github.com/shuhei1101/knowledge/issues/44)）で文書を YAML に移した後も、タグやメタデータで規約を引く手段が無い。
MCP を HTTP に統一する規約と既定のポートは [#50](https://github.com/shuhei1101/knowledge/issues/50) で入っている。
スキーマ・参照の検査のツールと CI は、#64 のレビューでこの Issue に含めると決まった（[コメント](https://github.com/shuhei1101/knowledge/pull/64#discussion_r4367269018)）。
knowledge のワークスペース `tmp/mcpベストプラクティス検討` の D-59〜D-61・D-82〜D-85 と、ドキュメント用 MCP のインターフェース定義 A-14 で決めた。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と影響する UC 一覧 |
| [反映作業](./反映作業/index.yaml) | この端末でのサーバーの起動とプラグインの導入 |

対象システムごとの計画書は、初期構築でアーキテクチャ図のサブシステムを決めた後に追加する。

## タスク一覧

- [ ] 初期構築（アーキテクチャ図・非機能要件・設計書の置き場所。コードを持つのはこの PR が初めて）
- [x] ~~リバースエンジニアリング~~（設計書も実装も無く、起こす対象が無い）
- [x] ~~方針決め~~（方針決めを依頼する Issue ではない）
- [x] ~~PoC 検証~~（未検証の技術機構に依存しない。会話キーを入れるフックは rule-inject の `session_id_injection` で、HTTP の MCP のプラグインは ai-monitor・observability で動いている）
- [ ] 複合ユースケース設計
- [x] ~~デザインスタイル選定~~（画面は mdmark の共通スタイルで描くと決まっている（D-85））
- [ ] 画面一覧・画面遷移
- [ ] 単一ユースケース設計
- [ ] モック作成
- [ ] インターフェース定義設計
- [ ] 部品設計
- [ ] 画面設計
- [ ] モジュール構成設計
- [ ] ドキュメント修正（要件.md の `## 更新ドキュメント`）
- [ ] 単体テスト作成
- [ ] 実装
- [ ] 結合テスト作成
- [ ] E2E テスト作成