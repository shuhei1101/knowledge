# GitHub Pages を Actions のワークフローで公開分の文書だけ配信する形へ切り替える

## 概要

利用者が GitHub Pages で、knowledge の `visibility: public` の文書だけを HTML で読めるようになる。
Pages は master へのマージで動く Actions のワークフローが作った成果物を配信し、YAML の原本と `visibility: internal` の文書は成果物に入れない。

## 背景

[Issue #69](https://github.com/shuhei1101/knowledge/issues/69) の要望。
今の Pages はブランチ master の `/docs` をそのまま配信している（build_type: legacy）。
[#64](https://github.com/shuhei1101/knowledge/pull/64)（[#44](https://github.com/shuhei1101/knowledge/issues/44)）で `docs/` の文書を YAML の正本へ移したため、develop が master へ入ると Pages の画面から文書が読めなくなる。
#64 のレビューで、[#51](https://github.com/shuhei1101/knowledge/issues/51) に含めず別の Issue にすると決まった（[コメント](https://github.com/shuhei1101/knowledge/pull/64#discussion_r4367269018)）。
#51 は develop を配信する開発ドキュメントサーバーで、この作業は master へのマージで動く Pages の配信のため、配信先と契機が違う。
配信の分担はユーザーが話し合いの L-12・D-30・D-55 で決めている。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と影響する UC 一覧 |
| [CI](./CI.md) | CI の計画書 |
| [検査と変換のスクリプト](./検査と変換のスクリプト.md) | 検査と変換のスクリプトの計画書 |
| [文書](./文書.md) | 文書の計画書 |
| [反映作業](./反映作業/index.yaml) | Pages の配信元の切り替え |

## タスク一覧

- [x] ~~初期構築~~（既存リポジトリのため対象外）
- [x] ~~リバースエンジニアリング~~（現状設計書が揃っている）
- [x] ~~方針決め~~（方針決めを依頼する Issue ではない）
- [x] ~~PoC 検証~~（Pages の Actions の配信と mdmark の `build` は既存の機構で、未検証の技術機構に依存しない）
- [x] ~~複合ユースケース設計~~（影響なし: 端末に導入して規約を引く流れは dev-docs で完結し、Pages を通らない）
- [x] ~~デザインスタイル選定~~（見た目は mdmark の共通スタイルで描き、knowledge は見た目を決めない）
- [x] ~~画面一覧・画面遷移~~（画面と画面遷移は mdmark の `build` が作る HTML が持ち、knowledge は画面を作らない）
- [x] 単一ユースケース設計
- [x] ~~モック作成~~（knowledge は画面を作らない）
- [x] インターフェース定義設計
- [x] ~~部品設計~~（画面の部品は mdmark が持つ）
- [x] ~~画面設計~~（画面の UI 項目は mdmark が持ち、knowledge の変更は画面の UI 項目を増やさない）
- [x] モジュール構成設計
- [x] ドキュメント修正（要件.md の `## 更新ドキュメント`）
- [x] 単体テスト作成
- [x] 実装
- [x] 結合テスト作成
- [x] E2E テスト作成
