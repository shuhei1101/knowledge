# agent-flow.example.md

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| ID | brain/stream/on-event |
| 概要 | コメントと状態を取得し、次の一手を決めて演出指示書を書き込む |
| 実行条件 | 「次へ」を受けたとき |
<!-- /table -->

## 工程

### コメントを取得する

**本文**: 選別済みで未読のコメントを取得する

**呼ぶもの**

<!-- table: {"kind": "data"} -->
| 種類 | MCP サーバー | ツール | 引数の制約 |
| --- | --- | --- | --- |
| mcp | MCP-1# | search | required: ['kind', 'unread']、properties: {'kind': {'const': 'comment'}, 'unread': {'const': True}} |
<!-- /table -->

### キャラクター情報を取得する

**埋め込む工程**: shared/character-state#steps[キャラクター情報を取得する]

### 演出指示書を書き込む

**本文**: 次の一手を決め、演出指示書を書き込む

**呼ぶもの**

<!-- table: {"kind": "data"} -->
| 種類 | MCP サーバー | ツール | 引数の制約 |
| --- | --- | --- | --- |
| mcp | MCP-1# | write_direction_memo | required: ['segment_id', 'memo'] |
<!-- /table -->
