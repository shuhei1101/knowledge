# SKILL.md の自動生成を廃止し、SKILL.md を設計書を見ながら記載するファイルにする

## 概要

knowledge の SKILL.md の自動生成（`scripts/build_skills.py`）と、全ての文書の検査の SKILL.md と生成元の比較を廃止し、SKILL.md をスキルの設計書を見ながら記載するファイルにする。

## 背景

[Issue #543](https://github.com/shuhei1101/knowledge/issues/543) は、SKILL.md の生成を [shuhei1101/project-index#243](https://github.com/shuhei1101/project-index/pull/243) の `project-index skill-md` へ切り替える要望だった。
ユーザーの判断（[コメント](https://github.com/shuhei1101/knowledge/pull/544#issuecomment-7074367837)）で、設計書から SKILL.md を自動生成すること自体をやめ、設計書と SKILL.md の二重管理にすることになった。

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.mark.md) | 要望の整理 |
| [文書](./文書.mark.md) | 配信元の設定とスキルのエージェントフローの置き場所の計画書 |
| [検査と変換のスクリプト](./検査と変換のスクリプト.mark.md) | 生成のコマンドの廃止と全ての文書の検査の計画書 |
