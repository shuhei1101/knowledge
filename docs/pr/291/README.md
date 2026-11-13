# dev-docs.yaml の設計書の行の検証と目次の作り直し・用語集の新設・空の hooks の扱い・設計書の検査を原本のスキーマへ切り替える

## 概要

knowledge の設計書を原本の `schemas/design/` のスキーマで検査し、書き込みのときに AI Monitor の設計書の検証と目次の作り直しを走らせる。
あわせて用語集を新設して複数のリポジトリで同じ意味で使用する呼び名を登録し、フックを持たない `hooks/` の扱いを決める。

## 背景

[#290](https://github.com/shuhei1101/knowledge/issues/290) は、`dev-docs.yaml` を触る次の 4 件を 1 本の作業 PR で行う束。

| Issue | 背景 |
| --- | --- |
| [#256](https://github.com/shuhei1101/knowledge/issues/256) | 設計書と目次の行は AI Monitor の検証を呼ばず、設計書は YAML の直接編集とコマンドで確かめている（[#253](https://github.com/shuhei1101/knowledge/pull/253) のレビューの任意の指摘から切り出し） |
| [#259](https://github.com/shuhei1101/knowledge/issues/259) | 規約『タグと用語の登録』は用語集 `terms.yaml` がある前提で書かれているが、用語集のファイルも `alias_type` の用語の行も無い（[#257](https://github.com/shuhei1101/knowledge/pull/257) のスコープ外から切り出し） |
| [#282](https://github.com/shuhei1101/knowledge/issues/282) | `hooks/hooks.json` は `{"hooks": {}}` だけで、フックを 1 つも登録していないのに `dev-docs.yaml` の `hooks` の行と画面の「フック」のグループが残る |
| [#283](https://github.com/shuhei1101/knowledge/issues/283) | 設計書は `schemas/` 直下の AI Monitor の配布物のコピーで検査している。設計書のスキーマはコピーを持たず knowledge の原本 1 つにすると決まっており（D-22 A、関係 shuhei1101/ai-monitor#3188）、#268・#279 を統合した |

## 計画書

| ファイル | 中身 |
| --- | --- |
| [要件](./要件.md) | 要望の整理 |
| [要件.yaml](./要件.yaml) | 影響するユースケース・更新ドキュメント・スコープ外 |
| [タスク一覧.yaml](./タスク一覧.yaml) | 工程ごとの状態 |
| [文書](./文書.md) | 文書の計画書 |
| [検査と変換のスクリプト](./検査と変換のスクリプト.md) | 検査と変換のスクリプトの計画書 |
| [反映作業](./反映作業/index.yaml) | 反映作業の一覧 |
