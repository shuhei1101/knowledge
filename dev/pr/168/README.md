# E2E が組み立てる files.yaml の行の文書の ID とページの path を、dev-docs の拡張子付きの ID に合わせる

## 概要

E2E が、files.yaml の行の文書を dev-docs の今の ID とページの path で開き・検索し、develop で通るようにする。

## 背景

[Issue #166](https://github.com/shuhei1101/knowledge/issues/166) の不具合。
E2E『利用者が画面で knowledge の文書を読む』が develop でも失敗し、files.yaml の行のページ（`hooks`・`scripts`・`skills`）が 404（`DocumentNotFoundError`）になる。
作業 PR [#162](https://github.com/shuhei1101/knowledge/pull/162) のレビューで、reviewer が対象外の逸脱として[報告](https://github.com/shuhei1101/knowledge/pull/162#discussion_r4456518275)した。
dev-docs は [shuhei1101/dev-docs#83](https://github.com/shuhei1101/dev-docs/pull/83)（[4b40256](https://github.com/shuhei1101/dev-docs/commit/4b4025672a2086367f12e7aa5ea22c9fef62d1cc)）で、`id` を持たない文書の ID を拡張子付きのパスにした。
E2E は、この変更の前（[e2d9e97](https://github.com/shuhei1101/knowledge/commit/e2d9e97c3a833f98545a5d43d3ddaf5456a3014b)）の拡張子なしの形式で ID とページの path を組み立てている。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と影響する UC 一覧 |
| [文書](./文書.md) | 文書の配信の E2E の計画書 |

## タスク一覧

- [x] ~~初期構築~~（既存リポジトリのため対象外）
- [x] ~~リバースエンジニアリング~~（シナリオが揃っている）
- [x] ~~方針決め~~（方針決めを依頼する Issue ではない）
- [x] ~~PoC 検証~~（未検証の技術機構に依存しない）
- [x] ~~複合ユースケース設計~~（シナリオの記述は ID とページの path の形式を持たず、変わらない）
- [x] ~~デザインスタイル選定~~（利用者に見える画面を変えない）
- [x] ~~画面一覧・画面遷移~~（利用者に見える画面を変えない）
- [x] ~~単一ユースケース設計~~（シナリオの記述は ID とページの path の形式を持たず、変わらない）
- [x] ~~モック作成~~（利用者に見える画面を変えない）
- [x] ~~インターフェース定義設計~~（スクリプトのインターフェースを変えない）
- [x] ~~部品設計~~（変更が画面に及ばない）
- [x] ~~画面設計~~（変更が画面に及ばない）
- [x] ~~モジュール構成設計~~（スクリプトの物理ファイルを変えない）
- [x] ~~ドキュメント修正~~（更新するドキュメントが無い）
- [x] ~~単体テスト作成~~（スクリプトを変えない）
- [x] ~~実装~~（スクリプトを変えない。修正は E2E のテストコードだけ）
- [x] ~~結合テスト作成~~（スクリプトを変えない）
- [x] E2E テスト作成
