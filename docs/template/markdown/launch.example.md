# ブレインノードの起動

claude-balancer のコンテナで、プロジェクトを参照させずに起動する

**ID**: LCH-1

**エージェント**: AG-1#

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| 種類 | service |
| 起動の依頼 | IF-31# |
<!-- /table -->

**コンテナ**: CTN-1#services[brain]

**システムプロンプト**: brain/system

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| 許可のモード | bypassPermissions |
<!-- /table -->

## フック

<!-- table: {"kind": "data"} -->
| イベント | 対象 | スクリプト | 目的 |
| --- | --- | --- | --- |
| SessionStart | clear\|compact | containers/brain/hooks/session_start.py | clear・圧縮のときに、返却済みの記録の削除を依頼する |
<!-- /table -->

## 環境変数

<!-- table: {"kind": "data"} -->
| 名前 | 値 |
| --- | --- |
| TZ | Asia/Tokyo |
<!-- /table -->

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| 秒数 | 60 |
| 導き方 | published_spec |
<!-- /table -->

## 終了したときの扱い

<!-- table: {"kind": "data"} -->
| 理由 | 扱い |
| --- | --- |
| rate_limit | wait_and_restart |
| authentication_failed | retry_once |
| claude_exited | retry_once |
| lease_expired | retry_once |
| stopped | stop |
<!-- /table -->

**関連**

<!-- table: {"kind": "data"} -->
| 相手の ID | 関係の種類 | いつ参照するか |
| --- | --- | --- |
| AG-1 | part_of | 起動の構成を変えるときに、起動するエージェントの定義と突き合わせる。 |
| MCP-1 | references | 許可するツールを変えるときに、MCP サーバーのツールの一覧を確認する。 |
<!-- /table -->
