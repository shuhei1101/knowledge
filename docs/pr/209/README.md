# 使い方『規約の索引を当てる』を、rule-inject が既定のパスの設定ファイルを参照する手順へ追従させる

## 概要

knowledge の規約を案内させたい利用者が、`env` を書かずに rule-inject の既定のパスの設定ファイルへ索引を記載する手順で、規約の索引を当てられるようにする。

## 背景

[Issue #191](https://github.com/shuhei1101/knowledge/issues/191) の要望。
[PR #190](https://github.com/shuhei1101/knowledge/pull/190)（起点 [Issue #184](https://github.com/shuhei1101/knowledge/issues/184)）で規約『Claude プラグインルール』の `settings-file-02` を「既定のパスと違う場所に置くときだけ `env` に `{ツール名}_CONFIG` を書く」に変え、使い方の追従を後続として切り出した。
rule-inject は [rule-inject#105](https://github.com/shuhei1101/rule-inject/issues/105)（[rule-inject PR #106](https://github.com/shuhei1101/rule-inject/pull/106)）で、`RULE_INJECT_CONFIG` が無くても `${XDG_CONFIG_HOME:-~/.config}/rule-inject/settings.yaml` を参照するようになり、`RULE_INJECT_INDEXES_USER` を廃止した。
使い方『規約の索引を当てる』は、まだ `env` の `RULE_INJECT_INDEXES_USER`・`RULE_INJECT_CONFIG` を書く手順になっている。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と影響する UC 一覧 |
| [確認ログ](./確認ログ.md) | ユーザーへの確認事項の決着 |

## タスク一覧

- [x] ~~初期構築~~（[#6](https://github.com/shuhei1101/knowledge/pull/6) で済んでいる）
- [x] ~~リバースエンジニアリング~~（使い方の文書だけで、起こす対象が無い）
- [x] ~~方針決め~~（方針決めを依頼する Issue ではない）
- [x] ~~PoC 検証~~（使い方の文書だけで、未検証の技術機構に依存しない）
- [x] ~~複合ユースケース設計~~（使い方の文書だけで、ユースケースが無い）
- [x] ~~デザインスタイル選定~~（利用者に見える画面の見た目を変えない）
- [x] ~~画面一覧・画面遷移~~（利用者に見える画面の見た目を変えない）
- [x] ~~単一ユースケース設計~~（使い方の文書だけで、ユースケースが無い）
- [x] ~~モック作成~~（利用者に見える画面の見た目を変えない）
- [x] ~~インターフェース定義設計~~（コードを変更しない）
- [x] ~~部品設計~~（変更が画面に及ばない）
- [x] ~~画面設計~~（変更が画面に及ばない）
- [x] ~~モジュール構成設計~~（コードを変更しない）
- [x] ドキュメント修正（要件.md の `## 更新ドキュメント`）
- [x] ~~単体テスト作成~~（コードを変更しない）
- [x] ~~実装~~（コードを変更しない）
- [x] ~~結合テスト作成~~（コードを変更しない）
- [x] ~~E2E テスト作成~~（コードを変更せず、ユースケースが無い）
