# 件数に比例して繰り返す処理を追加する変更に、最大の件数と上限の記載を求めるレビューの確認観点を追加する

## 概要

レビューする人が、件数に比例して繰り返す処理を追加する変更で、想定する最大の件数・その件数での上限・その件数で確認するテストの 3 つがあるかを確認できるようにする。

## 背景

[Issue #517](https://github.com/shuhei1101/knowledge/issues/517) の要望。
件数に比例して繰り返す処理が小さいデータのテストだけを通ってマージされ、実物の大きさで画面や応答が止まる不具合が続いた（[shuhei1101/mdmark#725](https://github.com/shuhei1101/mdmark/issues/725)・[shuhei1101/dev-docs#301](https://github.com/shuhei1101/dev-docs/issues/301)・[shuhei1101/mindstella#547](https://github.com/shuhei1101/mindstella/issues/547)）。
今のレビューのチェックシートは、実測しないと決定できない値に測った記録があること（[レビューの共通観点](https://github.com/shuhei1101/knowledge/blob/ee4db47/docs/checksheet/checksheet-review-common.yaml)）は求めるが、件数に比例して繰り返す処理を追加する変更を見つけて最大の件数と上限を求める観点を持たない。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.mark.md) | 要望の整理 |
| [文書](./文書.mark.md) | 文書の計画書 |
