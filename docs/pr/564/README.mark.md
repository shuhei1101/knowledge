# dev-docs のメタデータの画面から直コミットしてよい種類を direct_commit.kinds に追加する

## 概要

利用者が、dev-docs のメタデータの画面で knowledge の種類の表を修正し、その場で直コミットできるようになる。

## 背景

[Issue #563](https://github.com/shuhei1101/knowledge/issues/563) の要望。
[shuhei1101/dev-docs#310](https://github.com/shuhei1101/dev-docs/issues/310)（作業 PR [shuhei1101/dev-docs#313](https://github.com/shuhei1101/dev-docs/pull/313)、マージ済み）で、メタデータの画面と、編集中の変更を project-index の書き込みの API で直コミットする経路ができた。
画面で種類の表を修正できるのは、配信元の設定の `direct_commit.kinds[]` と端末の設定の `sources[].direct_commit.write_api_kinds` の両方に種類があるときで、knowledge の `project-index.yaml` は [#536](https://github.com/shuhei1101/knowledge/issues/536) で決めた `[knowhow, word-list, terms]` のまま。

[#536](https://github.com/shuhei1101/knowledge/issues/536) の「決まったこと」で、ユーザーは規約などのほかの種類を今までどおり Issue と作業 PR で登録すると決めた。
その後の [shuhei1101/dev-docs#310](https://github.com/shuhei1101/dev-docs/issues/310) の「決まったこと」で、データとメタデータを直コミットの対象にし、規約の本文は行の追加と文言の修正だけを対象にし、テンプレートとスキーマは今のまま、と決めた。
この作業は両方の決定を前提にし、#536 の決定から逸脱する種類を許可するかはユーザーへ確認する。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.mark.md) | 要望の整理と、追加する種類の論点 |
| [文書](./文書.mark.md) | 文書のサブシステム（配信元の設定・シナリオ・アーキテクチャ図・README）の計画書 |
