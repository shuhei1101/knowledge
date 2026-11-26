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

## ファイル一覧

<!-- table: {"kind": "data", "columns": {"補足": {"width": {"mode": "nowrap"}}}} -->
| ファイル | 管理する値 | 補足 |
| --- | --- | --- |
| {ファイル} | {管理する値} | {補足} |
<!-- /table -->

## キー一覧

<!-- table: {"kind": "data", "columns": {"説明": {"width": {"mode": "nowrap"}}}} -->
| キー | 論理名 | ファイル | 型 | 必須 | 条件 | 既定値 | 説明 | 欠落時の挙動 | 環境変数名 | 秘密 | 反映 | 許可する値や範囲 | 関連 | 検討事項 | 理由 | 状態 | 公開 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| {キー} | {論理名} | {ファイル} | {型} | true / false | {条件} | {既定値} | {説明} | {欠落時の挙動} | {環境変数名} | true / false | immediate / reload / restart | {許可する値や範囲} | to: {相手の ID}、item: {項目のパス}、type: requires / references / replaces / part_of / change_together、when: {いつ参照するか}、paths: ['{対象のパス}'] | {検討事項} | {理由} | planned / implemented / deprecated / removed | user / developer |
<!-- /table -->

## 環境ごとの差分

<!-- table: {"kind": "data", "columns": {"説明": {"width": {"mode": "nowrap"}}, "補足": {"width": {"mode": "nowrap"}}}} -->
| ファイル | キー | 値 | 説明 | 補足 |
| --- | --- | --- | --- | --- |
| {ファイル} | {キー} | {値} | {説明} | {補足} |
<!-- /table -->

**関連**

<!-- table: {"kind": "data"} -->
| 相手の ID | 項目のパス | 関係の種類 | いつ参照するか | 対象のパス |
| --- | --- | --- | --- | --- |
| {相手の ID} | {項目のパス} | requires / references / replaces / part_of / change_together | {いつ参照するか} | {対象のパス} |
<!-- /table -->

**検討事項**

- {検討事項}
