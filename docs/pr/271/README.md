# 設計書を作成する目的の記載・判定フローチャート『フォルダの中身の種類の決め方』・言語に依らないログの規約を追加する

## 概要

設計書を作成する目的、フォルダ構成の設計書のエントリに付ける中身の種類の決め方、言語に依らないログの規約を、knowledge の規約・判定フローチャートとして参照できるようにする。

## 背景

[Issue #270](https://github.com/shuhei1101/knowledge/issues/270) は、同じタグ（`kind:規約の更新`）で `scope:` が重なる計画の未着手の行を束ねた親 Issue。

| 子 | 要望 | 既存との関係 |
| --- | --- | --- |
| [#215](https://github.com/shuhei1101/knowledge/issues/215) | 設計書を作成する目的を「設計」で検索できる場所に記載する | 規約『設計原則』（`dev-design-principles`）はコードの設計原則だけを扱い、設計書を作成する理由はどの規約にも無い。依存の [#210](https://github.com/shuhei1101/knowledge/issues/210) は close 済み |
| [#225](https://github.com/shuhei1101/knowledge/issues/225) | 判定フローチャート『フォルダの中身の種類の決め方』を追加する | [#219](https://github.com/shuhei1101/knowledge/issues/219)（close 済み）で `schemas/design/layout.schema.yaml` に `content_types` が入ったが、どの単語を付けるかの決め方が無い |
| [#232](https://github.com/shuhei1101/knowledge/issues/232) | 言語に依らないログの規約を作る | レベルの表は言語ごとのロガーの規約（`python-shared-logger`・`react-shared-logger-implementation`）だけが持つ。移し元は [shuhei1101/ai-monitor#2328](https://github.com/shuhei1101/ai-monitor/issues/2328) |

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [要件.yaml](./要件.yaml) | 影響するユースケース・更新ドキュメント・スコープ外 |
| [タスク一覧.yaml](./タスク一覧.yaml) | 工程ごとの状態 |
| [文書](./文書.md) | サブシステム「文書」の計画書 |
