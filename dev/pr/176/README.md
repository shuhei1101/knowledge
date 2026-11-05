# tmux でのサーバーの立て方の規約を新設し、rules.yaml の登録の基準と claude・dev・テンプレートの規約を見直す

## 概要

どのリポジトリのセッションでも knowledge の規約が案内されるようにし、案内する規約を強制注入の 4 つの基準に絞る。
あわせて、tmux でのサーバーの立て方の規約を新設し、Markdown・YAML の検査ツールを CI に追加し、claude・dev・テンプレートの規約の矛盾と古い記述を修正する。

## 背景

[Issue #82](https://github.com/shuhei1101/knowledge/issues/82) の要望。
React 移行の話し合い（A-11・A-14・A-16）で決めた内容で、各リポジトリの React 移行の前提になる。

- knowledge の `rules.yaml` は、AI Monitor のエージェントのセッションには `RULE_INJECT_CONFIG` の設定ファイルで渡るが、利用者の 10 個の Claude Code の設定の `RULE_INJECT_INDEXES_USER` はすべて ai-monitor の `rules.global.yaml` を指し、knowledge を作業フォルダにしたセッション以外では参照されない
- `rules.yaml` には、末尾の `*` で `.json`・`.python-version`・設計書の `xxx.ts.yaml` に当たる glob、全ファイル・全 `.md` に当たるエントリ、一度も当たらない glob が残っている
- ローカルサーバーの立て方の規約が無く、tmux の外に置き去りのサーバーが 8 個ある。テンプレート『セットアップ手順』の `has-session`・`kill-session` は `=` を付けていない
- claude・dev・markdown・テンプレートの規約に、古い記述・矛盾・二重管理がある

python・html・ui・next・React の領域は [#79](https://github.com/shuhei1101/knowledge/issues/79)・[#80](https://github.com/shuhei1101/knowledge/issues/80)・[#81](https://github.com/shuhei1101/knowledge/issues/81)、`markdown-mermaid`・`markdown-flowchart`・`template-flowchart` は [#132](https://github.com/shuhei1101/knowledge/issues/132)、MCP の常駐サーバーの規約は [#74](https://github.com/shuhei1101/knowledge/issues/74) で対応済み。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と影響する UC 一覧 |
| [文書](./文書.md) | 文書の計画書 |
| [CI](./CI.md) | CI の計画書 |

## タスク一覧

- [x] ~~初期構築~~（既存リポジトリのため対象外）
- [x] ~~リバースエンジニアリング~~（設計書が揃っている）
- [x] ~~方針決め~~（方針決めを依頼する Issue ではない）
- [x] PoC 検証
- [x] ~~複合ユースケース設計~~（文書の検査が増えるだけで、ユースケースの流れを変えない）
- [x] ~~デザインスタイル選定~~（利用者に見える画面を変えない）
- [x] ~~画面一覧・画面遷移~~（画面の追加・削除と画面遷移の変更を含まない）
- [x] 単一ユースケース設計
- [x] ~~モック作成~~（利用者に見える画面を変えない）
- [x] インターフェース定義設計
- [x] ~~部品設計~~（変更が画面に及ばない）
- [x] ~~画面設計~~（変更が画面に及ばない）
- [x] モジュール構成設計
- [x] ドキュメント修正（要件.md の `## 更新ドキュメント`）
- [ ] 単体テスト作成
- [ ] 実装
- [ ] 結合テスト作成
- [ ] E2E テスト作成
