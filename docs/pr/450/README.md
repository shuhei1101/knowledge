# knowledge の既存の文書に残る AI slop の 12 単語を対応表の置き換え先へ置き換える

## 概要

knowledge の文書（`docs/`・`schemas/`）に残る AI slop の 12 単語（入口・入り口・終わり・地・帯・受け口・外の・許す・通し・新しい／新しく・決まる・古い）を、対応表の置き換え先へ置き換える。

## 背景

[#399](https://github.com/shuhei1101/knowledge/issues/399) の要望。
[#397](https://github.com/shuhei1101/knowledge/pull/397)（起点 Issue [#394](https://github.com/shuhei1101/knowledge/issues/394)）で AI slop の対応表 `docs/word-list/word-list-ai-slop.yaml` に 12 単語の行を追加したが、既存の文書にはこれらの単語が残っている。
`check_all.py` は文書の本文を対応表で検査しないため既存の文書の検査は落ちないが、エージェントが文書を読んで書き写すと slop-check の通知が増える。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | サブシステム「文書」の計画書 |
