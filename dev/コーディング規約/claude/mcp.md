# MCP サーバー作成ルール

## SDK とトランスポート

- 公式 MCP Python SDK（pip の `mcp` パッケージ）の `MCPServer` を使う
  - `from mcp.server.mcpserver import MCPServer`
  - 旧名の `FastMCP`（`mcp.server.fastmcp`）は v2 で削除された。サードパーティの「FastMCP」（pip の `fastmcp`）とも別物
- MCP サーバーは HTTP（Streamable HTTP）の常駐サーバーにする（`mcp.streamable_http_app()`）。stdio（`mcp.run()`）は禁止する
- stdio は **セッションごとに 1 プロセス**が立つ。5 セッション並べれば同じサーバが 5 個起動し、依存解決も 5 回走る。並行で起動するセッションの数だけプロセスが増える
- Claude Code の MCP 起動は既定でノンブロッキング。接続中のサーバーのツールが要るときは、Claude が接続完了を待つ
- 毎ターン使うツールを持つサーバーだけ `.mcp.json` に `"alwaysLoad": true` を付ける。ツール検索を介さず最初のプロンプトから載り、起動がツールの確定まで待つ（上限は `MCP_CONNECT_TIMEOUT_MS`）
- 常駐サーバをどう起動するかを決める。既に常駐しているプロセス（アプリ本体・compose のサービス）に相乗りさせると、起動するものが増えない
- HTTP は 1 プロセスを複数セッションが共有するため、ツール関数はモジュール変数に状態を持たせない

## 構成

- ロジックの置き場所はツールの重さで決める
  - 外部 API を 1 回叩く程度の薄い操作は、サーバーファイルに直接書いてよい。
    subprocess を挟むと起動コストと引数の受け渡しが増えるだけで得るものがない
  - 分岐・状態管理を伴う処理は `scripts/` や `tools/` の単体実行可能な CLI に切り出し、サーバーはそれを呼ぶだけにする。
    CLI 単体でデバッグでき、ロジックが MCP に縛られない
- 常駐サーバーには、セッションの作業ディレクトリと環境変数（`CLAUDE_PROJECT_DIR`・`CLAUDE_CODE_SESSION_ID`）が渡らない
  - サーバーが持つファイルは、作業ディレクトリに依存せず、起動時に設定したルートを基準にパス解決する
  - セッションの作業対象のファイルは、ツールの引数で絶対パスを受ける。セッションごとの値は PreToolUse フックで引数に入れる

## サーバーとツールの単位

- 文書の置き場所（リポジトリ）ごとにサーバーを 1 つにする
  分けるのは、置き場所・権限・リリースの単位が違うときだけ
- ツールは操作（検索・取得・書き込み・差分・タグの一覧・スキーマの取得）で分け、文書の種類は `kind` の enum 引数で指す
  種類ごとのツールを作らない
- 種類ごとの違い（スキーマ・独自の検査・返す形式・読み書きの場所）は、サーバーの中で `kind` ごとのハンドラーに振り分ける
- 操作の意味が種類に固有のものと、削除など rule-inject や権限で止めたい操作だけ、別のツールにする

## mdmark と YAML の正本・MCP の役割の分担

- YAML の正本と、それを扱う MCP・開発ドキュメントサーバーは、文書を持つ各プロジェクトが持つ
- mdmark は Markdown の記法と共通スタイルの描画だけを受け持ち、YAML を読まない
  用語集の表の印など Markdown の機能は mdmark に残す
- 配信するときは、各プロジェクトのスクリプトが YAML を mdmark の記法の Markdown に変換し、mdmark で描く
- mdmark と YAML の正本・MCP は互いに依存せず、使う側のプロジェクトが両方を取り入れる

## ツール定義のスキーマ

<!-- table: data -->

| 要素 | 書き方 |
| --- | --- |
| description | 関数の docstring（1 行） |
| title | `@mcp.tool(title="日本語タイトル")` |
| 引数の説明 | `Annotated[型, Field(description=...)]` |
| 引数の選択肢制限 | `Literal[...]` → enum としてスキーマに反映 |
| 出力スキーマ | 型付きで返すツールだけ、戻り値を Pydantic モデルにする → outputSchema 自動生成。各フィールドに `Field(description=...)` |
| ツールの性質 | `ToolAnnotations(readOnlyHint=..., destructiveHint=...)` |

<!-- /table -->

- 型付きで返すツールの戻り値は `{success: bool, output: str}` 形式の共通モデルを基本とする
- Markdown・YAML を見せるツールは `str` を返し、outputSchema を出さない
  Claude Code は structuredContent があると text を読まない
- 型付きで返すツールは、structuredContent と text に同じ内容を入れる

## 読み取りのツール

- 種類ごとの `list_*` を作らず、絞り込みの引数を持つ `search` 1 つにまとめる
- 既定の `limit` を持ち、絞り込みに当たった総数 `total` を返す。続きがあるときは `next_cursor` を返す。型付きで返すツールは、どちらも共通モデルに項目を追加して返す
- `view`（`brief` / `standard` / `full`）で返す量を選べ、`include` / `exclude`（項目名の enum の配列）で追加・除外できるようにする。既定は `search` が `brief`、1 件を取るツールが `standard`。省いた項目は `omitted` で返し、取り方を添える
- `search` の `brief` は各行に ID・名前・概要文・タグ・文字数・バージョンを返し、中身は ID で取るツールで返す。結果の先頭に総件数と、当たった全件の合計文字数を返す
- 切り詰めたときは、`total` と返した件数に加えて、絞り込める引数を案内する
- 引数なしの `search` は、既定件数の先頭ページ・`brief`・タグごとの件数・総件数・`next_cursor` を返す
- `search` に任意の `count_only` を持たせ、一覧を返さずに総件数・合計文字数・タグごとの件数だけを返せるようにする
  手順で先に呼ぶことは強制せず、エージェントがヒットの多さを見て絞り込むときに使う
- タグの絞り込みは、主題のタグ（`main`）が一致した文書を上に並べる
- 1 件を取るツールは `ids` の配列で複数を受け、渡した順に返す
  合計が 50,000 文字を超えるときは 1 件も返さず、分けて呼ぶよう返す（Claude Code は 50,000 文字を超える結果をファイルに退避する）
  見つからない ID があれば全体を失敗にし、近い ID を添える
- 長い文書は、セクションごとの行範囲・文字数・ハッシュを返すツールを置き、セクションを指定して取得させる
- 一覧は Markdown の表（各行に ID と名前）、1 件の本文は Markdown（複数なら `<document>` で包む）、YAML が正本の項目は YAML のまま返す
  参照は ID と名前・概要文まで結合し、相手の本文は結合しない
- 本文に出る用語・エイリアスは、本文を変えずに末尾に一覧（語と ID）を付ける
  語の名前と概要文を引くツールを置く
- 用語・エイリアスの照合に使う語の一覧（語・正規化した語・ID・種類・概要・関連する文書）を返すツールを置く
  指定したバージョンから変わっていなければ、変わっていないことだけを返す
  mod が使うので、`format` の既定は `json` にする
- 読み取りのツールに `readOnlyHint` を付ける（Claude Code が並列に実行する）
- 読み取りのツールに共通の `format`（`markdown` / `json`、既定 `markdown`）を持たせる
  `json` のときは structuredContent と text に同じ JSON を入れ、`markdown` のときは structuredContent を返さない
- 会話キーは `session_id` と `agent_id` の別々の 2 つの引数で受け、PreToolUse フックが入れる
  エージェントには記載させない
- 1 つのセッションで同じ内容は 1 回だけ渡す
  対象は、関連に結合した相手の名前・概要文、1 件を取るツールの末尾の用語の一覧、同じバージョンの文書の本文
  サーバーは会話キーごとに返した内容のハッシュを記録し、2 回目は返し済みのマーカーだけを返す（用語の一覧は、返した語を省く）
  `repeat_seen` で再取得できるようにし、`/clear`・圧縮の後はフックで記録を捨てる
  会話キーが無いときは省かない
  検索結果の各行の概要文は、選ぶために使うので省かない
- 1 セッション 1 回の決まりは、MCP のツールに限らず、フック・mod で文脈を追加するときにも当てる
  入力に用語の文脈を追加するときは、そのセッションで初めて出た語だけ、語・ID・説明・関連する文書（ID と名前）を 1 回だけ追加する

出典: [Anthropic: Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)、[MCP 仕様: Tools](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)（`tools/list` の `cursor` / `nextCursor`）、[Google AIP-157](https://google.aip.dev/157)（view）、[anthropics/claude-code #9962](https://github.com/anthropics/claude-code/issues/9962)（structuredContent を優先し text を捨てる）、[MCP 仕様 2026-07-28: Changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)（接続を会話とみなさない）

## 差分のツール

- サーバーがエージェントの既読時点を記録し、`changes_since_read` で前回から変わった項目・キー・変更前の値を返す
  エージェントにバージョンを持たせない
- 区間（`from`・`to`）で追加・変更・削除された文書の一覧を返すツールを置く
  区間を自分で指すときは、`changes_since_read` ではなくこのツールを使う
  `include_diff` で文書ごとの差分も返す
- `from`・`to` は git の commit・日時・ブランチ・タグのどれでも受け、サーバーが commit に解決する
  日時はその時点の最後の commit にする
  解決した commit と日時を結果の先頭に返す
- 1 件を取るツールに差分モード（`diff_from`・`diff_to`・`context_lines`、既定 3）を持たせ、git と同じ `+`・`-` の行で返す
  `rev` だけの変化は出さず、参照の ID には名前を添える
  `format: json` のときは、変わったキーごとの変更前後の値と、本文の変わった行の配列を返す
- MCP の変更通知（resources の購読）には頼らない
  Claude Code は購読せず、通知はモデルに届かない

## 検索の手段

- 検索はタグ・メタデータ・キーワード（正規化と `aliases`）を基本にする
  ベクトル検索は必須にせず、ライブラリも指定しない
- 言い換えや関連の探索は、安いモデルのサブエージェントに検索のツールを使わせる
- ベクトル検索を追加するときは DB サーバーを立てず、埋め込みはメモリか Git の外のキャッシュに置く
  YAML と Git には入れない

## 関連と影響範囲のツール

- 全文書の ID・種類・概要文を返す骨組みのツールを置く
- ID を起点に関連・コード参照をたどり、影響する文書を理由つきで返すツールを置く
- 関連の候補は、同じコミットでの変更・同じ会話での編集・同じ会話での閲覧を分けて記録し、上位 3 件を概要文つきで出す
  採用されたものだけ文書の関連に記載する
- Issue の対応範囲は、骨組み → 用語集で言い換えたキーワードの検索 → 関連・コード参照のたどり → 変更の種類ごとのチェックリスト → 人の確認、の順で決める

## 登録

- プロジェクト用: ルートの `.mcp.json`（バージョン管理でチーム共有）。開発ドキュメントサーバーにつなぐ MCP は対象外
- プラグイン用: プラグインルートの `.mcp.json`
- 開発ドキュメントサーバーにつなぐ MCP は、各リポジトリを Claude Code のマーケットプレイスにし、プラグインで配る
  利用者は、どのプロジェクトでも使うならユーザースコープ、特定のプロジェクトだけならプロジェクトスコープで入れる
- 文書の MCP のプラグインは、文書を持つリポジトリごとに 1 つにし、ほかのプラグインと分ける
- 文書の MCP のプラグインの名前は `{リポジトリ}-docs` にする（例: `knowledge-docs`・`mdmark-docs`）

接続先を書く。

```json
{
  "mcpServers": {
    "my-tools": {
      "type": "http",
      "url": "http://127.0.0.1:${KNOWLEDGE_PORT:-8781}/mcp",
      "alwaysLoad": true
    }
  }
}
```

- `url` を書くときは `type` を添える。`type` の無いエントリは stdio として読まれ、サーバーごとスキップされる
- `url` は `http://127.0.0.1:${{リポジトリ}_PORT:-{既定のポート}}/mcp` の形式で書く。`{リポジトリ}_PORT` と `{既定のポート}` は次の台帳の環境変数と既定のポート
- ポートがぶつかるときだけ、`~/.claude/settings.json` の `env` に `{リポジトリ}_PORT` を書いて上書きする
- サーバーは起動時に同じ `{リポジトリ}_PORT` を読み、無ければ台帳の既定のポートで待ち受ける。上書きするときは、サーバーを起動する環境にも同じ値を渡す

既定のポートの台帳は次のとおり。

<!-- table: data -->

| リポジトリ | 環境変数 | 既定のポート |
| --- | --- | --- |
| observability | `OBSERVABILITY_PORT` | 8766 |
| ai-monitor | `AI_MONITOR_PORT` | 8767 |
| claude-balancer | `CLAUDE_BALANCER_PORT` | 8770 |
| knowledge | `KNOWLEDGE_PORT` | 8781 |
| mdmark | `MDMARK_PORT` | 8782 |
| rule-inject | `RULE_INJECT_PORT` | 8783 |
| MindStella | `MINDSTELLA_PORT` | 8784 |

<!-- /table -->

## 動作確認

- `mcp.list_tools()` を非同期実行し、全ツールの title・引数説明・enum・annotations が生成されることと、型付きで返すツールの outputSchema が生成されることを確認する
- 設定が変わらないプラグイン MCP サーバーは `/reload-plugins` で再接続されないので、反映にはセッション再起動が必要。`/mcp` で接続状態を確認する
