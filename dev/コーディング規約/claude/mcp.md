# MCP サーバー作成ルール

## SDK とトランスポート

- 公式 MCP Python SDK（pip の `mcp` パッケージ）の `MCPServer` を使う
  - `from mcp.server.mcpserver import MCPServer`
  - 旧名の `FastMCP`（`mcp.server.fastmcp`）は v2 で削除された。サードパーティの「FastMCP」（pip の `fastmcp`）とも別物

トランスポートは、同時に走るセッション数で選ぶ。

| トランスポート | 選ぶ条件 | 起動のされ方 |
| --- | --- | --- |
| stdio | 単一セッションから使う。手元で 1 つずつ動かす道具 | セッションごとに子プロセスが起動する（`mcp.run()`） |
| HTTP（Streamable HTTP） | 複数セッションが同時に叩く。常駐プロセスに相乗りできる | 常駐サーバへ接続するだけ（`mcp.streamable_http_app()`） |

- stdio は **セッションごとに 1 プロセス**が立つ。5 セッション並べれば同じサーバが 5 個起動し、依存解決も 5 回走る
- Claude Code の MCP 起動は既定でノンブロッキング。接続中のサーバーのツールが要るときは、Claude が接続完了を待つ
- 毎ターン使うツールを持つサーバーだけ `.mcp.json` に `"alwaysLoad": true` を付ける。ツール検索を介さず最初のプロンプトから載り、起動がツールの確定まで待つ（上限は `MCP_CONNECT_TIMEOUT_MS`）。上限に収まらないなら HTTP へ移す
- HTTP を選ぶときは常駐サーバをどう起動するかもセットで決める。既に常駐しているプロセス（アプリ本体・compose のサービス）に相乗りさせると、起動するものが増えない
- HTTP は 1 プロセスを複数セッションが共有するため、ツール関数はモジュール変数に状態を持たせない

## 構成

- ロジックの置き場所はツールの重さで決める
  - 外部 API を 1 回叩く程度の薄い操作は、サーバーファイルに直接書いてよい。
    subprocess を挟むと起動コストと引数の受け渡しが増えるだけで得るものがない
  - 分岐・状態管理を伴う処理は `scripts/` や `tools/` の単体実行可能な CLI に切り出し、サーバーはそれを呼ぶだけにする。
    CLI 単体でデバッグでき、ロジックが MCP に縛られない
- stdio のサーバープロセスの環境には `CLAUDE_PROJECT_DIR`（プロジェクトルート）と `CLAUDE_CODE_SESSION_ID` が渡される
  - 作業ディレクトリに依存せず `CLAUDE_PROJECT_DIR` を基準にパス解決する

## ツール定義のスキーマ

<!-- table: data -->

| 要素 | 書き方 |
| --- | --- |
| description | 関数の docstring（1 行） |
| title | `@mcp.tool(title="日本語タイトル")` |
| 引数の説明 | `Annotated[型, Field(description=...)]` |
| 引数の選択肢制限 | `Literal[...]` → enum としてスキーマに反映 |
| 出力スキーマ | 戻り値を Pydantic モデルにする → outputSchema 自動生成。各フィールドに `Field(description=...)` |
| ツールの性質 | `ToolAnnotations(readOnlyHint=..., destructiveHint=...)` |

<!-- /table -->

- 戻り値は `{success: bool, output: str}` 形式の共通モデルを基本とする

## 読み取りのツール

- 種類ごとの `list_*` を作らず、絞り込みの引数を持つ `search` 1 つにまとめる
- 既定の `limit` を持ち、絞り込みに当たった総数 `total` を返す。続きがあるときは `next_cursor` を返す
- `response_format`（`concise` / `detailed`）で返す量を選べるようにする。既定は `concise`
- 切り詰めたときは、`total` と返した件数に加えて、絞り込める引数を案内する

出典: [Anthropic: Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)、[MCP 仕様: Tools](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)（`tools/list` の `cursor` / `nextCursor`）

## 登録

- プロジェクト用: ルートの `.mcp.json`（バージョン管理でチーム共有）
- プラグイン用: プラグインルートの `.mcp.json` + `${CLAUDE_PLUGIN_ROOT}` でパス解決

stdio の場合は起動コマンドを書く。

```json
{
  "mcpServers": {
    "my-tools": {
      "command": "uv",
      "args": ["run", "--with", "mcp", "python", "${CLAUDE_PLUGIN_ROOT}/mcp/server.py"]
    }
  }
}
```

HTTP の場合は接続先を書く。

```json
{
  "mcpServers": {
    "my-tools": {
      "type": "http",
      "url": "http://localhost:8766/mcp",
      "alwaysLoad": true
    }
  }
}
```

- `url` を書くときは `type` を添える。`type` の無いエントリは stdio として読まれ、サーバーごとスキップされる

## 動作確認

- `mcp.list_tools()` を非同期実行し、全ツールの title・引数説明・enum・outputSchema・annotations が生成されることを確認する
- 設定が変わらないプラグイン MCP サーバーは `/reload-plugins` で再接続されないので、反映にはセッション再起動が必要。`/mcp` で接続状態を確認する
