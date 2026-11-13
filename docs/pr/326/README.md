# 設計書の AI slop の単語の修正・dev-docs の記述の project-index への書き換えと、フォルダ構成の設計書への生成元の記載をまとめて行う

## 概要

knowledge の設計書と使い方『文書の MCP を使う』が、文書の MCP・管理の MCP・配信元の登録を project-index、画面を dev-docs が持つ今の構成を表し、文に AI slop の単語を残さない。
フォルダ構成の設計書から、生成物の `README.md` と設計書の種類のテンプレートの `items` の生成元と、作り直すコマンドが分かる。

## 背景

[Issue #324](https://github.com/shuhei1101/knowledge/issues/324) は、次の 4 件をまとめた束の Issue。

- [#263](https://github.com/shuhei1101/knowledge/issues/263): PR #257 で書き換えなかった設計書の文に AI slop の単語が残っている（origin/develop の対応表のコピーの照合で 1333 件）
- [#280](https://github.com/shuhei1101/knowledge/issues/280): `docs/` の各フォルダの `README.md` を作り直すコマンドが開発コマンド CMD-72-1 に無く、フォルダ構成の設計書 LAY-72-1 に `generated_from` を記載できない
- [#281](https://github.com/shuhei1101/knowledge/issues/281): LAY-72-1 の `docs/template/` のエントリに、`items` の生成元と生成するコマンドが無い
- [#309](https://github.com/shuhei1101/knowledge/issues/309): [shuhei1101/project-index#15](https://github.com/shuhei1101/project-index/pull/15) と [shuhei1101/dev-docs#163](https://github.com/shuhei1101/dev-docs/pull/163)（どちらもマージ済み）で文書の MCP・管理の MCP・配信元の読み込みとプラグインが project-index へ移ったが、アーキテクチャ図・シナリオ・使い方に dev-docs が持つ記述が残っている

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [文書](./文書.md) | 設計書・使い方の計画書 |
