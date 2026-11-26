# 配信のブレインノード

配信を始めるときに起動し、配信の進行を決めるエージェント

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| ID | AG-1 |
| サブシステム | ARCH-1#subsystems[brain] |
| 識別子 | brain-stream |
<!-- /table -->

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| 起動方式 | tui |
| 寿命 | resident |
<!-- /table -->

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| モデルの ID | claude-opus-5-5 |
| 理由 | 進行の判断に推論の質が要るため |
<!-- /table -->

## きっかけ

<!-- table: {"kind": "data"} -->
| 名前 | メッセージ | シナリオ |
| --- | --- | --- |
| start | IF-11# | SC-3#scenarios[正常シナリオ] |
| external-event | IF-12# | SC-3#scenarios[正常シナリオ] |
<!-- /table -->

## 段階

<!-- table: {"kind": "data", "columns": {"説明": {"width": {"mode": "nowrap"}}}} -->
| 名前 | 手順の名前 | 説明 | きっかけ |
| --- | --- | --- | --- |
| startup | 起動時の手順 | 起動した直後 | start |
| on-event | イベントの手順 | 外部イベントを受けたとき | external-event |
| resume | 再開の手順 | 圧縮・再起動の後 |  |
| shutdown | 終了の手順 | 配信を終えるとき |  |
<!-- /table -->

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| MCP サーバー | MCP-1# |
| ツール | write_progress |
<!-- /table -->

## 番の初めの通知

<!-- table: {"kind": "data"} -->
| 名前 | 条件 | 内容 | 元にするデータ | 届け方 |
| --- | --- | --- | --- | --- |
| game-switched | 前の番の後に、遊んでいるゲームが切り替わった | 切り替わったことと、切り替えた後のゲームの概要 | DATA-3# | via: tool_result、server: MCP-1#、tool: fetch_utterances |
| speech-stopped | 前の番の後に、再生中のセリフを止めて、残りの文がある | 止めたセリフと、話していない残りの文 |  | via: input |
<!-- /table -->

**関連**

<!-- table: {"kind": "data"} -->
| 相手の ID | 関係の種類 | いつ参照するか |
| --- | --- | --- |
| SC-3 | requires | エージェントの段階を変えるときに、シナリオの流れと突き合わせる。 |
<!-- /table -->
