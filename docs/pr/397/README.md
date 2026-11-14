# 話し合いで指摘した 12 単語（入口・終わり・地・帯・受け口・外の・許す・通し・新しく決まること・新しい・決まる・古い）を AI slop の対応表に追加する

## 概要

エージェントが 12 単語（入口・終わり・地・帯・受け口・外の・許す・通し・新しく決まること・新しい・決まる・古い）を記載したとき、プラグイン slop-check が NG として通知し、置き換え先を示す。

## 背景

[Issue #394](https://github.com/shuhei1101/knowledge/issues/394) の要望。
利用者が 2026-11-05 から 2026-11-14 に、話し合いのスレッドでこの 12 単語を 1 件ずつ指摘した。
対応表 `docs/word-list/word-list-ai-slop.yaml` にこれらの行が無く、slop-check が通知しない。
前回の追加は [#200](https://github.com/shuhei1101/knowledge/pull/200)（Issue [#196](https://github.com/shuhei1101/knowledge/issues/196)）。
受付のレビューの任意の指摘（[task-reviewer のコメント](https://github.com/shuhei1101/knowledge/issues/394#issuecomment-6879902917)）で、既存の行 `toosu`（通す）・`furui`（旧い）との重なりを着手時に決めることになった。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | 対応表の計画書 |
| [slop-check](./slop-check.md) | 対応表のコピーの計画書 |
