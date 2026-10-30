---
name: text-review
description: ファイル・フォルダ・Git のコミットで渡した範囲の文章を、knowledge の文章の規約に合わせて点検して修正する。文書やルールの文章を規約に揃えたいときに使う。
argument-hint: "<ファイルのパス | フォルダのパス | コミット | コミットの範囲>"
---

# 文章を点検して修正する

範囲は `$ARGUMENTS` で受ける。

## 手順

### 範囲をファイルに展開する

- ファイルのパスはそのファイルにする
- フォルダのパスは配下のファイルすべてにする
- パスとして存在しなければコミットかコミットの範囲として扱い、`git diff-tree --no-commit-id --name-only -r --diff-filter=d {コミット}` か `git diff --name-only --diff-filter=d {範囲}` で変わったファイルにする
- 文章でないファイル（画像・バイナリ）は除く

### ファイルが無いときは返して終える

展開したファイルが 0 件なら、規約を読まずに、渡した範囲と見つからないことを出して終える。

### 規約を読む

次の規約を読む。
『ユーザ配下ルール記載時の規約』は、範囲に `.claude/rules/` のファイルがあるときだけ読む。

| 規約 | ID |
| --- | --- |
| 文章の書き方 | `convention-writing-style` |
| 既存文章の維持 | `convention-keep-existing-text` |
| 論点の提示 | `convention-issue-presentation` |
| ドキュメントの部品 | `doc-parts` |
| ユーザ配下ルール記載時の規約 | `claude-rule-writing` |

- dev-docs の `search_docs`（`mcp__plugin_dev-docs_dev-docs__search_docs`）が使えるなら、`source` を `knowledge`、`filter` を `id` の `eq` で上の ID、`view` を `full` にして読む
- ツールが無い（ToolSearch で探しても無い）か、規約が見つからないなら、`${CLAUDE_PLUGIN_ROOT}/docs/rule/{ID}.yaml` を読む

### すべてを調べて修正する箇所の一覧を作る

すべてのファイルの本文を読み、規約に反する箇所を、ファイル・箇所・当てる規約・修正後の文で一覧にする。
一覧を作り終えるまで、ファイルは修正しない。

### まとめて修正する

一覧が空なら修正しない。
空でなければ、一覧の箇所をまとめて修正する。

### サマリーを出す

ファイルごとに、修正した箇所・当てた規約・件数を出す。
一覧が空なら「修正する箇所はありませんでした」を出す。
