# {タイトル}

{冒頭リード}

**ID**: {ID}

**公開範囲**: public / internal

**タグ**

<!-- table: {"kind": "data"} -->
| タグの名前 | 主題 |
| --- | --- |
| {タグの名前} | true / false |
<!-- /table -->

**別名**

- {別名}

**エージェント**: {エージェント}

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| 種類 | service / command |
| 起動の依頼 | {起動の依頼} |
| コマンド | {コマンド} |
<!-- /table -->

**コンテナ**: {コンテナ}

**システムプロンプト**: {システムプロンプト}

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| 許可のモード | bypassPermissions / dontAsk / acceptEdits / auto / manual / plan |
<!-- /table -->

## フック

<!-- table: {"kind": "data"} -->
| イベント | 対象 | スクリプト | 目的 |
| --- | --- | --- | --- |
| {イベント} | {対象} | {スクリプト} | {目的} |
<!-- /table -->

## 環境変数

<!-- table: {"kind": "data"} -->
| 名前 | 値 | 秘匿値の配置先 |
| --- | --- | --- |
| {名前} | {値} | {秘匿値の配置先} |
<!-- /table -->

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| 秒数 | {秒数} |
| 導き方 | measured_p999 / published_spec / no_output / measured_x10 |
| 導出の元の値 | {導出の元の値} |
<!-- /table -->

## 終了したときの扱い

<!-- table: {"kind": "data"} -->
| 理由 | 扱い |
| --- | --- |
| {理由} | wait_and_restart / retry_once / stop |
<!-- /table -->

**関連**

<!-- table: {"kind": "data"} -->
| 相手の ID | 項目のパス | 関係の種類 | いつ参照するか | 対象のパス |
| --- | --- | --- | --- | --- |
| {相手の ID} | {項目のパス} | requires / references / replaces / part_of / change_together | {いつ参照するか} | {対象のパス} |
<!-- /table -->

**検討事項**

- {検討事項}
