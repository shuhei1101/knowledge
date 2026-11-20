# ネットミームと作品の種類・スキーマ・検査を、直コミットを許可する別の配信元として追加する

## 概要

ネットミームと、その元になる作品を、knowledge のリポジトリの中の規約とは別の配信元に、project-index で検索できる文書として持てるようにする。
許可した作業場所からは、直コミットで登録できるようにする。

## 背景

[Issue #514](https://github.com/shuhei1101/knowledge/issues/514) の要望。
aituber の動画のセリフに入れるネットミームを登録して検索するデータが無い。
MindStella の話し合い（[追記のコメント](https://github.com/shuhei1101/knowledge/issues/514#issuecomment-7031184832)）でデータの構造と登録の方法を決めたが、配置する種類とスキーマが knowledge に無い。
直コミットは [shuhei1101/project-index#210](https://github.com/shuhei1101/project-index/pull/210) で project-index に入り、v0.2.0 でリリースされた。
登録のスキル・エージェントフロー・知名度の判定表と最初の登録は [#526](https://github.com/shuhei1101/knowledge/issues/526) が行う。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.mark.md) | 要望の整理 |
| [文書](./文書.mark.md) | 文書のサブシステム（スキーマ・配信元の設定・設計書・使い方）の計画書 |
| [検査と変換のスクリプト](./検査と変換のスクリプト.mark.md) | 検査と変換のスクリプトのサブシステムの計画書 |
