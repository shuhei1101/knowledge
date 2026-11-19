# slop-check の検知の画面への表示を設定で切り替えられるようにし、既定を表示しないにする

## 概要

プラグイン slop-check が検知した単語を利用者の画面に出す 1 行（`systemMessage`）を、設定で切り替えられるようにし、既定を表示しないにする。
モデルへの通知（`additionalContext`）は、設定に関係なく今のまま出す。

## 背景

[#504](https://github.com/shuhei1101/knowledge/issues/504) の要望。
[#338](https://github.com/shuhei1101/knowledge/pull/338) で、slop-check のフックはヒットがあれば常に `systemMessage` に `AI slop を検知: {単語}（{ツール}）` を出すようになった。
この表示はデバッグのために確認しているもので普段の利用では要らないが、slop-check には表示を止める設定（端末ごとの設定ファイル・環境変数）が無い。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [slop-check](./slop-check.md) | サブシステム「slop-check」の計画書 |
| [文書](./文書.md) | サブシステム「文書」の計画書 |
| [反映作業](./反映作業/index.yaml) | 反映作業の一覧 |
