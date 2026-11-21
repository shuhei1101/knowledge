# SKILL.md の生成を project-index skill-md へ切り替え、独自の生成のコマンドを廃止する

## 概要

knowledge の SKILL.md の生成と検査を `project-index skill-md` へ切り替え、knowledge 独自の生成のコマンド（IF-312-1）と、全ての文書の検査の SKILL.md と生成元の比較を廃止する。

## 背景

[Issue #543](https://github.com/shuhei1101/knowledge/issues/543) の要望。
[shuhei1101/project-index#243](https://github.com/shuhei1101/project-index/pull/243) で、`docs/agent-flow/` の `type: skill` のエージェントフローから SKILL.md を生成・検査する `project-index skill-md`（project-index の IF-37）が入った。
knowledge は同じ約束で SKILL.md を組み立てる `scripts/build_skills.py`（IF-312-1）を持ち、project-index・knowledge・rule-inject に実装が並ぶため、書式の約束を変えるたびに 3 か所を合わせる必要がある。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.mark.md) | 要望の整理 |
| [文書](./文書.mark.md) | 配信元の設定とスキルのエージェントフローの置き場所の計画書 |
| [検査と変換のスクリプト](./検査と変換のスクリプト.mark.md) | 生成のコマンドの廃止と全ての文書の検査の計画書 |
