# レビューのチェックシートの残りの 15 ページの観点を、1 件 = 1 要素の成果物の種類・工程のタグ付きの構造へ書き換える

## 概要

レビューするエージェントが、`checksheet-review-common` 以外のレビューのチェックシートの観点も、成果物の種類・工程のタグで `search_docs` を絞って 1 件ずつ取得できるようになる。

## 背景

[Issue #577](https://github.com/shuhei1101/knowledge/issues/577) の要望。
[#580](https://github.com/shuhei1101/knowledge/pull/580)（[Issue #576](https://github.com/shuhei1101/knowledge/issues/576)）で、チェックシートのスキーマに観点の配列 `aspects` を、`project-index.yaml` に観点を 1 件ずつ配信する種類 `review_aspect` の行を追加し、`checksheet-review-common` を書き換えた。
残りの 15 ページは観点を `items[]` の 1 項目の Markdown の表で持ったままで、`review_aspect` の文書にならない。
後続の [shuhei1101/ai-monitor#3828](https://github.com/shuhei1101/ai-monitor/issues/3828) が、この作業の後に reviewer の knowledge の観点の参照の手順を書き換える。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.mark.md) | 要望の整理 |
| [文書](./文書.mark.md) | 15 ページの観点の書き換えの計画書 |
