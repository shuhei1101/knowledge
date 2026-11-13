# 規約『見積もりポイント』を AI が作業する前提（分割を求めない・1 件の Issue の最大 20 pt）に作成し直す

## 概要

Issue を見積もる人（planner・task-planner）が、AI が作業する前提の規約『見積もりポイント』で、分割せずにまとめた Issue を作れるようにする。

## 背景

[Issue #318](https://github.com/shuhei1101/knowledge/issues/318) の要望。
規約『見積もりポイント』（[docs/rule/dev-estimate-points.yaml](https://github.com/shuhei1101/knowledge/blob/develop/docs/rule/dev-estimate-points.yaml)）は人が作業する前提で、13 pt を「分割必須（スプリントに含めない）」にしている。
この記載が ai-monitor の task-planner・planner が Issue を細かく分ける根拠になっている。
AI は Issue ごとに設計書・規約・コードを読み直すため、分割するとその読み直しが Issue の数だけ増える。
後続の [shuhei1101/ai-monitor#3405](https://github.com/shuhei1101/ai-monitor/issues/3405) が、この規約の値（1 件の Issue の最大 20 pt・1 Sprint 50 pt）を使う。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理と変更箇所の由来 |
| [文書](./文書.md) | 文書の計画書 |
