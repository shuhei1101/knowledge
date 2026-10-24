# YAML

YAML を扱う決まり。
データの正本の持ち方、スキーマの書き方、検査、書き込み、MCP からの書き込みと読み取りを定める。

## データの正本

データの正本を DB に持たないプロジェクトに適用する。

### 概要

- 新規ドメインのデータ管理は YAML を SoT として持ち、`index.yaml` + `settings.yaml` の 2 レイヤー構成を使う ことを必須化する。
- frontend / backend が同じ YAML を見て同じ識別子で実装できることと、Claude Code がデータの全貌を 1 箇所で把握できる
  - 散らばらない ことが目的。

### 必須化する 2 レイヤー構成

| ファイル                  | 役割                                                | git        | 編集経路              |
| ------------------------- | --------------------------------------------------- | ---------- | --------------------- |
| `**/index.yaml`           | キー本体 — 環境非依存 / 構造定義 / 一覧性が要るもの | committed  | 手編集                |
| `**/settings.yaml`        | 付随メタデータ — 画面から更新する / 環境別 / 個人差 | gitignored | UI または手編集       |
| `**/settings.sample.yaml` | `settings.yaml` の committed template               | committed  | 手編集 (新キー追加時) |

#### どちらに書くかの判断

- 利用者が画面から変える → `settings.yaml`
- ファイル追加と同時に増える本質的なキー → `index.yaml`
- git で全員揃ってほしい値 → `index.yaml` または `settings.sample.yaml`

「画面更新もなく環境依存もない」単独 YAML (例: `content/banned_words.yaml`) は 2 レイヤーにせず単独 YAML で OK。
2 レイヤーが必須になるのは「画面から更新」or「環境別」が発生するとき。

アプリの設定値（接続先・環境ごとの値・ブランチで試す値）の置き場所は [設定値の置き場所](../../判定フローチャート/設定値の置き場所.md) が決め、既定値 → 環境の値 → checkout の上書き の 3 レイヤーに重ねる。
このセクションの `settings.yaml` は画面から更新するデータのファイルで、3 レイヤーの環境の値（`~/.config/{project}/settings.yaml`）とは別。
`content/` に置く、形式を問わない正本の置き場所は [コンテンツの置き場所](./コンテンツの置き場所.md) が決める。

### frontend / backend は同じ YAML を読む

- 物理 ID と論理名 を YAML 1 箇所で定義し、Python / JS の両方が YAML を返す API 経由で同じ値を取る
- コード内ハードコード禁止 — YAML に未登録のキーが必要になったら YAML を先に更新する
- 表記が乖離する事故を構造的に潰すのが目的

### worktree-safe な runtime YAML

`settings.yaml` 等、実行時に UI / API から書き込まれる YAML は、どの worktree から書いても main repo の同一ファイル に着地させる。
worktree 削除でユーザーデータが消える事故 を防ぐため。

以下例では (`main_repo_root()` ヘルパ) を採用:

```python
from {pkg}.shared.paths import main_repo_root
path = main_repo_root() / "config" / "settings.yaml"
```

## スキーマ

YAML の構造は、種類ごとにスキーマの YAML で定義する。
プロジェクトが構造を決めてアプリが読み込む YAML（データの正本・`content/` の YAML・プロンプト）に当てる。
外部のツールが構造を決める YAML（CI・compose など）と、`pydantic-settings` で読む設定（[設定](../python/shared/設定.md)）には当てない。

- JSON Schema 2020-12 で書く
- ファイル名は `{種類}.schema.yaml`（例 `プロンプト.schema.yaml`）にする
- 各項目に `title`・`description` を付け、スキーマを読めば各項目に何を書くかが分かるようにする
- 種類をまたぐ型は `共通.schema.yaml` の `$defs` に置き、各スキーマから `$ref` で指す
- フロー形式（`{type: string, ...}`）を使わず、ブロック形式で書く

## 検査

読み込むとき（起動の事前確認など）に、`## スキーマ` を当てる全ての YAML をスキーマに通す。

- 違反は `{ファイル}: {キーのパス}: {理由}` の行で全て並べる
- ファイルを書き換えずに違反を並べるだけの検査のツールを置く
- スキーマで見られない決まり（ID の重複・参照の実在・mermaid の文法など）は独自の検査に記載し、スキーマの検査と 1 つの検査のツールにまとめる
- mermaid は `@probelabs/maid` で検査する
  自動修正（`--fix`）は意味を変えることがあるので使わない

## 書き込み

プログラム（MCP・アプリの UI / API・ローカルの開発 DB など）が YAML を書くときは、次を守る。

- 書き込む前に、変更を当てた後の中身を `## 検査` に通し、1 件でも違反があれば何も書き換えずにエラーを返す
- 一時ファイルに書いてから置き換える
- 複数のファイルを書く途中で失敗したら、置き換えた分を元に戻す
- 読み込み・検査・書き込みを排他ロックの中で行う

## MCP からの書き込み

YAML を書き込む MCP のツールがあるプロジェクトでは、YAML を直接編集せず MCP から書き込む。

- 書き込みは `## 書き込み` に従う
- 書き込むツールの説明（入力の名前・型・必須・書くべき中身）は、スキーマの `title`・`description`・必須から組み立てる
- 書き込みに項目の `expected_version`（`rev`）を必須にし、合わなければ書かずに、再読み込みして再度呼び出すよう返す
  バージョンはファイルではなく項目ごとに持つ
- 違反のエラーは `isError` で返す
  `dry_run` で書かずに検査と差分だけを返せるようにする
- 返り値は新しいバージョン・短い差分・検査の結果にし、全文を返さない

## MCP からの読み取り

読み取りのツールの作り方は [MCP サーバー作成ルール](../claude/mcp.md) の `## 読み取りのツール` に従う。
YAML では次を追加する。

- タグの一覧を YAML に登録する。登録外のタグは弾かずに未登録の候補として受け付け、検査で警告する（[タグと用語の登録](./タグと用語の登録.md)）
- タグの一覧のツールを置き、登録したタグごとに名前・説明・そのタグを持つ項目の数・使っている種類を返す。数が 0 のタグも返す。`query` を受け、正規化した名前・`aliases`・説明に一致するタグを上位から返す
- 検索のタグは複数を渡せ、既定は全てを持つ項目（AND）に絞る。どれかを持つ項目（OR）は別の引数（`any_tags`）で渡す
- 登録外のタグで検索したら、近い候補を添えたエラーにする
- 読み取りのツールの説明も、スキーマから組み立てる。使える絞り込みと、タグの一覧のツールは語彙が多いときに呼ぶこと（引数なしの `search` がタグごとの件数を返す）を記載する

## 出典

- [Anthropic: Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)（入出力の説明）
- [MCP 仕様: Tools](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)（`inputSchema` / `outputSchema`）
- [JSON Schema 2020-12: Core](https://json-schema.org/draft/2020-12/json-schema-core)（`$ref`・`$defs`）
- [JSON Schema 2020-12: Validation](https://json-schema.org/draft/2020-12/json-schema-validation)（`title`・`description`）
