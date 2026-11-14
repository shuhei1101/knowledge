---
name: text-review
description: ファイル・フォルダ・Git のコミットで指定した範囲の文章を knowledge の文章の規約に合わせて点検して修正し、結果をサマリーで返却するスキルで、文書やルールの文章を規約に統一したいときに使用する
argument-hint: <ファイルのパス | フォルダのパス | コミット | コミットの範囲>
arguments:
- range
allowed-tools:
- Bash(git diff-tree *)
- Bash(git diff *)
---

<!-- docs/skill/text-review.yaml から生成した。このファイルを修正せず、設計書を修正して再生成する -->

# 文章を点検して修正する

## 引数

| 引数 | 説明 |
| --- | --- |
| `$range` | 点検する範囲。ファイルのパス・フォルダのパス（配下をすべて）・Git のコミットかコミットの範囲（変わったファイル）のどれでもよい |

## 手順

### 範囲をファイルに展開する

- ファイルのパスはそのファイルにする
- フォルダのパスは配下のファイルすべてにする
- パスとして存在しなければコミットかコミットの範囲として扱い、変わったファイルにする
- 文章でないファイル（画像・バイナリ）は除く

呼ぶもの:

- コマンド `git diff-tree --no-commit-id --name-only -r --diff-filter=d {コミット}`
- コマンド `git diff --name-only --diff-filter=d {範囲}`

### ファイルが無いときは返却して終える

展開したファイルが 0 件のときだけ行う。

規約を参照せずに、指定した範囲と見つからないことを出して終える。

### 規約を参照する

次の規約を参照する。
『ユーザ配下ルール記載時の規約』は、範囲に `.claude/rules/` のファイルがあるときだけ参照する。

| 規約 | ID |
| --- | --- |
| 文章の書き方 | `convention-writing-style` |
| 既存文章の維持 | `convention-keep-existing-text` |
| 論点の提示 | `convention-issue-presentation` |
| ドキュメントの部品 | `doc-parts` |
| ユーザ配下ルール記載時の規約 | `claude-rule-writing` |

- project-index か dev-docs の `search_docs` を使用できるなら、そのツールで参照する
  - 引数は `source` を `knowledge`、`filter` を `id` の `eq` で上の ID、`view` を `full` にする
  - project-index のツールの完全名は `mcp__plugin_project-index_project-index__search_docs`
  - dev-docs のツールの完全名は `mcp__plugin_dev-docs_dev-docs__search_docs`
- どちらのツールも無いか、規約が見つからないなら、`${CLAUDE_PLUGIN_ROOT}/docs/rule/{ID}.yaml` を参照する

呼ぶもの:

- ツール `Read`

### すべてを調べて修正する箇所の一覧を作る

すべてのファイルの本文を参照し、規約に反する箇所を、ファイル・箇所・適用する規約・修正後の文で一覧にする。
一覧を作り終えるまで、ファイルは修正しない。

呼ぶもの:

- ツール `Read`

### まとめて修正する

一覧が空でないときだけ行う。

一覧の箇所をまとめて修正する。

呼ぶもの:

- ツール `Edit`

### サマリーを出す

ファイルごとに、修正した箇所・適用した規約・件数を出す。
一覧が空なら「修正する箇所はありませんでした」を出す。
