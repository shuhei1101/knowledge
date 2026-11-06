# React の設定ファイルへ規約を案内する rules.yaml の行と、画面の状態の保持先の判定フローチャート・スクロール位置の決まりを追加する

## 概要

React のフロントエンドの設定ファイル（`shared/styles/` の CSS・`tsconfig.json`・`package.json`・`eslint.config.js`）を編集するときに、Tailwind・ビルド・lint の規約が案内されるようにする。
画面の一時的な状態の保持先をスタックによらない判定フローチャートで選べ、戻る・進む・リンクでの入り直し・タブの切り替えでのスクロール位置と状態の決まりを規約で参照できるようにする。

## 背景

[Issue #207](https://github.com/shuhei1101/knowledge/issues/207) の束（[#189](https://github.com/shuhei1101/knowledge/issues/189)・[#199](https://github.com/shuhei1101/knowledge/issues/199)）の要望。

- #189: claude-balancer の [PR #229](https://github.com/shuhei1101/claude-balancer/pull/229) で React の SPA を作ったとき、`frontend/src/shared/styles/*.css`・`tsconfig.json`・`package.json`・`lefthook.yml` にルールが注入されず、`eslint.config.js` には `dev-coding-general` だけが注入された。プロジェクト側の索引は knowledge のルールを指せないため、knowledge の `rules.yaml` で対応する（[確認事項](https://github.com/shuhei1101/claude-balancer/pull/229#discussion_r4482782615)）。[#158](https://github.com/shuhei1101/knowledge/issues/158) から移した範囲で、#158 の [PR #204](https://github.com/shuhei1101/knowledge/pull/204) はこの 3 件を `rules.yaml` に記載せずにマージした
- #199: 規約『入力と文言』の `state-retention-01` はスクロール位置を sessionStorage の 1 行で扱い、ページ全体と画面の中のスクロール領域を分けず、戻るとリンクでの入り直しも分けていない。規約『URL の状態』と判定フローチャート『React の状態の置き場所』の `q2`・`q8` も同じく混ざっており、React 以外の画面で参照できる判定フローチャートが無い。その結果、mdmark のビュワーと MindStella の画面が、戻る・タブの切り替えでスクロール位置を失う。後続は shuhei1101/mdmark#338・shuhei1101/mindstella#452

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と影響する UC 一覧 |
| [文書](./文書.md) | 文書の計画書 |

## タスク一覧

- [x] ~~初期構築~~（既存リポジトリのため対象外）
- [x] ~~リバースエンジニアリング~~（設計書が揃っている）
- [x] ~~方針決め~~（方針決めを依頼する Issue ではない）
- [x] ~~PoC 検証~~（未検証の技術機構に依存しない。`paths` の当たり方は rule-inject の MCP の索引のチェックで確認する）
- [x] ~~複合ユースケース設計~~（影響なし: 文書の登録・検索・書き込みの流れを変えない）
- [x] ~~デザインスタイル選定~~（利用者に見える画面を変えない）
- [x] ~~画面一覧・画面遷移~~（画面の追加・削除と画面遷移の変更を含まない）
- [x] ~~単一ユースケース設計~~（影響なし: 規約・判定フローチャート・索引の行の追加と修正で、シナリオの記述を変えない）
- [x] ~~モック作成~~（利用者に見える画面を変えない）
- [x] ~~インターフェース定義設計~~（スクリプトの入出力を変えない）
- [x] ~~部品設計~~（変更が画面に及ばない）
- [x] ~~画面設計~~（変更が画面に及ばない）
- [x] ~~モジュール構成設計~~（スクリプトを変えない）
- [ ] ドキュメント修正（要件.md の `## 更新ドキュメント`）
- [x] ~~単体テスト作成~~（スクリプトを変えない）
- [x] ~~実装~~（スクリプトを変えない）
- [x] ~~結合テスト作成~~（スクリプトを変えない）
- [x] ~~E2E テスト作成~~（シナリオの記述を変えない）
