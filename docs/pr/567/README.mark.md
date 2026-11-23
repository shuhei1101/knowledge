# エージェントフローのスキーマの工程に、識別子・ゲート・案の作成者・単位の種類のキーを追加する

## 概要

どのプロジェクトでも、エージェントフローの工程に識別子・ゲート・案の作成者・単位の種類を記載して、knowledge のスキーマの検査に合格させられるようにする。

## 背景

[Issue #566](https://github.com/shuhei1101/knowledge/issues/566) の要望。
[shuhei1101/aituber#228](https://github.com/shuhei1101/aituber/pull/228)（台本作成ノードの進め方の文書）で、工程ごとのエージェントゲート・ヒューマンゲート・案を出す作成者・単位の種類を工程に記載する案 A にユーザーが決めた（[確認事項への回答](https://github.com/shuhei1101/aituber/pull/228#discussion_r4664258566)）。
今の工程（`$defs/step`）は `additionalProperties: false` で、このキーを記載すると検査で不合格になる。
shuhei1101/aituber#228 は、この作業 PR で作成する `design-schemas/v*` のタグを待っている。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.mark.md) | 要望の整理 |
| [文書](./文書.mark.md) | 文書の計画書 |
