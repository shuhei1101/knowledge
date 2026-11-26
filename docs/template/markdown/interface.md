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

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| 種類 | endpoint / mcp_tool / operation / trigger / screen |
| 値 | {値} |
| 呼び出し API | {呼び出し API} |
<!-- /table -->

<!-- table: {"kind": "plain", "collapse": {"open": false}} -->
| 対応テストファイル |
| --- |
| `{対応テストファイル}` |
<!-- /table -->

- {実装のファイル}

<!-- table: {"kind": "plain"} -->
| 項目 | 値 |
| --- | --- |
| 識別子 | {識別子} |
| 必要な権限 | {必要な権限} |
| 冪等 | true / false |
| 読み取りだけ | true / false |
| 破壊的 | true / false |
| 副作用 | {副作用} |
<!-- /table -->

**呼び出し元**

- {参照}

**排他**: {排他}

## リクエスト

<!-- table: {"kind": "data", "columns": {"説明": {"width": {"mode": "nowrap"}}, "補足": {"width": {"mode": "nowrap"}}}} -->
| パラメータ | 型 | 必須 | 条件 | デフォルト | 配置場所 | 説明 | 制限 | 形式 | 例 | 空を許可 | 補足 | 状態 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| {パラメータ} | {型} | true / false | {条件} | {デフォルト} | path / query / header / cookie / body / argument | {説明} | {制限} | {形式} | {例} | true / false | {補足} | planned / implemented / deprecated / removed |
<!-- /table -->

<!-- tabs -->

## リクエスト例

{リクエスト例}

<!-- /tabs -->

## レスポンス

<!-- table: {"kind": "data", "columns": {"説明": {"width": {"mode": "nowrap"}}, "補足": {"width": {"mode": "nowrap"}}}} -->
| フィールド | 型 | 条件 | 説明 | 制限 | 形式 | 例 | 補足 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| {フィールド} | {型} | {条件} | {説明} | {制限} | {形式} | {例} | {補足} |
<!-- /table -->

<!-- tabs -->

## レスポンス例

{レスポンス例}

<!-- /tabs -->

**レスポンスの注記**: {レスポンスの注記}

## ステータスコード

<!-- table: {"kind": "data", "columns": {"補足": {"width": {"mode": "nowrap"}}}} -->
| ステータスコード | 発生条件 | 補足 |
| --- | --- | --- |
| {ステータスコード} | {発生条件} | {補足} |
<!-- /table -->

## 例外

<!-- table: {"kind": "data", "columns": {"補足": {"width": {"mode": "nowrap"}}}} -->
| 例外 | 発生条件 | 補足 |
| --- | --- | --- |
| {例外} | {発生条件} | {補足} |
<!-- /table -->

**エラーの形式**: {エラーの形式}

## 制約

<!-- table: {"kind": "data", "columns": {"補足": {"width": {"mode": "nowrap"}}}} -->
| 項目 | 制約 | 決定値 | 補足 |
| --- | --- | --- | --- |
| {項目} | {制約} | {決定値} | {補足} |
<!-- /table -->

## 全体の流れ

{全体の流れ}

## フロー

### {フロー名}

**概要**: {概要}

#### セットアップ

<!-- table: {"kind": "data", "columns": {"説明": {"width": {"mode": "nowrap"}}, "補足": {"width": {"mode": "nowrap"}}}} -->
| セットアップ | 説明 | 補足 |
| --- | --- | --- |
| {セットアップ} | {説明} | {補足} |
<!-- /table -->

#### フロー

{フロー}

#### 期待値

- {期待値}

**テスト**: {テスト}

**関連**

<!-- table: {"kind": "data"} -->
| 相手の ID | 項目のパス | 関係の種類 | いつ参照するか | 対象のパス |
| --- | --- | --- | --- | --- |
| {相手の ID} | {項目のパス} | requires / references / replaces / part_of / change_together | {いつ参照するか} | {対象のパス} |
<!-- /table -->

**検討事項**

- {検討事項}

**関連**

<!-- table: {"kind": "data"} -->
| 相手の ID | 項目のパス | 関係の種類 | いつ参照するか | 対象のパス |
| --- | --- | --- | --- | --- |
| {相手の ID} | {項目のパス} | requires / references / replaces / part_of / change_together | {いつ参照するか} | {対象のパス} |
<!-- /table -->

**検討事項**

- {検討事項}
