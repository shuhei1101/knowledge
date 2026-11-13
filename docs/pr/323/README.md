# Git フックと CI で動かすものの決まりと 0.x の間は develop だけで開発する運用を規約に追加し、ドキュメントサイトを develop から出す

## 概要

規約に、Git フックと CI で lint・型検査・テストを動かさず生成・配布に当たるものだけを動かす決まりと、0.x の間は develop だけで開発する運用を追加し、ドキュメントサイトを develop から出す。

## 背景

[#321](https://github.com/shuhei1101/knowledge/issues/321) は [#227](https://github.com/shuhei1101/knowledge/issues/227) と [#230](https://github.com/shuhei1101/knowledge/issues/230) の束。
フックの検査はエージェントの手順の lint・テストと重なり、2026-11-08 にユーザーが各リポジトリの lefthook から検査を削除した。
0.x の間の運用は ai-monitor の規約『ブランチ戦略』『バージョニング』（[shuhei1101/ai-monitor#3377](https://github.com/shuhei1101/ai-monitor/pull/3377)）を正として追随する。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
