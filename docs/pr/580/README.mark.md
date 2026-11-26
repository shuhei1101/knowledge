# レビューのチェックシートの観点を 1 件 = 1 文書の成果物の種類・工程のタグ付きの構造にし、タグで取得できるようにする

## 概要

レビューするエージェントが、knowledge のレビューのチェックシート（`checksheet-review-*`）の観点を、成果物の種類・工程のタグで `search_docs` を絞って、変更に該当する観点だけを取得できるようになる。

## 背景

[Issue #576](https://github.com/shuhei1101/knowledge/issues/576) の要望。
`checksheet-review-*` は観点を `items[]` の 1 項目の Markdown の表で持ち、配信の行（`project-index.yaml` の `checksheet`）は 1 ファイル = 1 文書のため、観点は ID でページ単位に参照するしかない。
AI Monitor は [shuhei1101/ai-monitor#3826](https://github.com/shuhei1101/ai-monitor/pull/3826) で固有の観点を観点 1 件 = 1 要素の `target:`・`process:` のタグ付きの YAML に移し、`records: aspects` の行で 1 件ずつ配信した。
後続の [shuhei1101/ai-monitor#3828](https://github.com/shuhei1101/ai-monitor/issues/3828) が、この作業の後に reviewer の knowledge の観点の参照の手順を書き換える。
残りの 15 ページの書き換えは [#577](https://github.com/shuhei1101/knowledge/issues/577) が受け持つ。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.mark.md) | 要望の整理 |
| [文書](./文書.mark.md) | スキーマ・配信の行・`checksheet-review-common` の書き換えの計画書 |
| [検査と変換のスクリプト](./検査と変換のスクリプト.mark.md) | knowledge-checks・knowledge-markdown・全ての文書の検査の対応の計画書 |
