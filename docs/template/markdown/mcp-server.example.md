# aituber の MCP

記録を検索・取得・書き込みする

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| ID | MCP-1 |
| サーバー名 | aituber |
| リポジトリ | shuhei1101/aituber |
<!-- /table -->

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| 種類 | http |
| URL | http://127.0.0.1:{AITUBER_PORT}/mcp |
<!-- /table -->

## ツール

<!-- table: {"kind": "data"} -->
| 名前 | インターフェース定義 |
| --- | --- |
| search | IF-21# |
| write_progress | IF-22# |
<!-- /table -->

## クライアント

### AG-1#

**許可するツール**

- search
- write_progress

**入れる引数**

<!-- table: {"kind": "data"} -->
| 引数 | 値の参照先 |
| --- | --- |
| cwd | source: session、name: cwd |
| session_id | source: session、name: session_id |
<!-- /table -->

### AG-2#

**許可するツール**

- search

**ヘッダー**

<!-- table: {"kind": "data"} -->
| 名前 | 値の参照先 |
| --- | --- |
| X-Aituber-Call-Id | source: call、name: call_id |
<!-- /table -->

**関連**

<!-- table: {"kind": "data"} -->
| 相手の ID | 関係の種類 | いつ参照するか |
| --- | --- | --- |
| AG-1 | references | ツールを追加・削除するときに、ツールを使用するエージェントの段階を確認する。 |
<!-- /table -->
