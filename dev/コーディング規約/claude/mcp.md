# MCP サーバー作成ルール

## SDK とトランスポート

- 公式 MCP Python SDK（pip の `mcp` パッケージ）の `FastMCP` を使う
  - `from mcp.server.fastmcp import FastMCP`
  - サードパーティの「FastMCP 2.0」（pip の `fastmcp`）とは別物。混同しない

トランスポートは、同時に走るセッション数で選ぶ。

| トランスポート | 選ぶ条件 | 起動のされ方 |
| --- | --- | --- |
| stdio | 単一セッションから使う。手元で 1 つずつ動かす道具 | セッションごとに子プロセスが起動する（`mcp.run()`） |
| HTTP（Streamable HTTP） | 複数セッションが同時に叩く。常駐プロセスに相乗りできる | 常駐サーバへ接続するだけ（`mcp.streamable_http_app()`） |

- stdio は **セッションごとに 1 プロセス**が立つ。5 セッション並べれば同じサーバが 5 個起動し、依存解決も 5 回走る
- Claude Code の MCP 起動は**既定でノンブロッキング**で、接続完了を待たずに最初のプロンプトを処理する。接続が間に合わないとツール一覧に載らず、モデルは「ツールが無い」と判断して代替手段（CLI 直叩き等）に流れる
- 接続に時間がかかる構成では `.mcp.json` に `"alwaysLoad": true` を付けてツール確定まで待たせる（上限 5 秒）。5 秒に収まらないなら HTTP へ移す
- HTTP を選ぶときは常駐サーバをどう起動するかもセットで決める。既に常駐しているプロセス（アプリ本体・compose のサービス）に相乗りさせると、起動するものが増えない
- HTTP は 1 プロセスを複数セッションが共有するため、ツール関数はモジュール変数に状態を持たせない

## 構成

- ロジックの置き場所はツールの重さで決める
  - 外部 API を 1 回叩く程度の薄い操作は、サーバーファイルに直接書いてよい。
    subprocess を挟むと起動コストと引数の受け渡しが増えるだけで得るものがない
  - 分岐・状態管理を伴う処理は `scripts/` や `tools/` の単体実行可能な CLI に切り出し、サーバーはそれを呼ぶだけにする。
    CLI 単体でデバッグでき、ロジックが MCP に縛られない
- サーバープロセスの環境には `CLAUDE_PROJECT_DIR`（プロジェクトルート）と `CLAUDE_CODE_SESSION_ID` が渡される
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
- docstring に引数説明を書かない（スキーマに反映されないため。必ず `Field` で書く）

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

- `url` を書くときは `type` を必ず添える。`type` の無いエントリは stdio として読まれ、サーバーごとスキップされる
- HTTP にするとプラグイン側は `.mcp.json` だけになり、ツールの修正にプラグイン再インストールが要らなくなる（常駐サーバの再起動で反映される）

## 動作確認

- `mcp.list_tools()` を非同期実行し、全ツールの title・引数説明・enum・outputSchema・annotations が生成されることを確認する
- 反映にはセッション再起動が必要（`/reload-plugins` ではプラグイン MCP サーバーは再接続されない場合がある。`/mcp` で接続状態を確認）
