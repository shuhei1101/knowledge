# ノウハウ・単語の対応表・用語集を、手元のセッションから直コミットで登録できるようにする

## 概要

knowledge のワークツリーの外部の手元のセッションが、`write_docs` の `commit` で、ノウハウ・単語の対応表・用語集を develop へ直コミットで登録できるようにする。

## 背景

[Issue #536](https://github.com/shuhei1101/knowledge/issues/536) の要望。
ノウハウ・AI slop の単語・用語を追加するたびに Issue を起票して作業 PR で登録しており、MindStella の話し合いで出たノウハウと単語が話し合いの表に溜まったままになっている。
直コミットは [shuhei1101/project-index#209](https://github.com/shuhei1101/project-index/issues/209) で project-index に入り、[#514](https://github.com/shuhei1101/knowledge/issues/514)（[#530](https://github.com/shuhei1101/knowledge/pull/530)）で配信元 `knowledge-memes` のネットミームと作品だけに許可した。
配信元 `knowledge` の `project-index.yaml` には `direct_commit` が無い。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.mark.md) | 要望の整理 |
| [文書](./文書.mark.md) | 文書のサブシステム（配信元の設定・設計書・使い方）の計画書 |
| [検査と変換のスクリプト](./検査と変換のスクリプト.mark.md) | 検査と変換のスクリプトのサブシステム（対応表のコピーの作成）の計画書 |
| [slop-check](./slop-check.mark.md) | プラグイン slop-check のサブシステムの計画書 |
