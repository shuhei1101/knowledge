# 行動選択ノード

選択肢から次の行動を 1 つ選ぶ

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| ID | LLM-1 |
| 呼び出す側 | ARCH-1#subsystems[virtual-life] |
| 種類 | choose |
<!-- /table -->

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| モデルの ID | jev-1 |
| 理由 | 選ぶだけなので速く安いモデルにする |
<!-- /table -->

**プロンプト**: virtual-life/choose_action

## 入力

<!-- table: {"kind": "data"} -->
| 変数名 | 取得元 |
| --- | --- |
| character_status | ER-1#tables[character_status] |
| options | ER-1#tables[action_options] |
<!-- /table -->

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| 選択肢の入力 | options |
| 上限 | 10 |
<!-- /table -->

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| 秒数 | 8 |
| 導き方 | measured_p999 |
| 導出の元の値 | p99.9 が 5.2 秒（1,200 回） |
<!-- /table -->

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| 回数の上限 | 2 |
| 間隔 | exponential_jitter |
<!-- /table -->

**関連**

<!-- table: {"kind": "data"} -->
| 相手の ID | 関係の種類 | いつ参照するか |
| --- | --- | --- |
| SC-5 | requires | 呼び出しの入力・出力を変えるときに、シナリオの流れと突き合わせる。 |
<!-- /table -->
